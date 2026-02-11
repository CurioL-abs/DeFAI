import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import {
  createMint,
  createAccount,
  mintTo,
  getAccount,
  TOKEN_PROGRAM_ID,
} from "@solana/spl-token";
import { PublicKey, Keypair, SystemProgram, SYSVAR_RENT_PUBKEY } from "@solana/web3.js";
import { expect } from "chai";

// Type will be generated after first build
// import { YieldVault } from "../target/types/yield_vault";

describe("yield_vault", () => {
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);

  const program = anchor.workspace.YieldVault as Program<any>;
  const owner = provider.wallet;

  let mint: PublicKey;
  let vaultPda: PublicKey;
  let vaultBump: number;
  let shareMintPda: PublicKey;
  let shareMintBump: number;
  let vaultTokenPda: PublicKey;
  let vaultTokenBump: number;

  // User token accounts
  let userTokenAccount: PublicKey;
  let userShareAccount: PublicKey;

  const VAULT_SEED = Buffer.from("vault");
  const SHARE_MINT_SEED = Buffer.from("share_mint");
  const VAULT_TOKEN_SEED = Buffer.from("vault_token");

  before(async () => {
    // Create underlying token mint (e.g. fake USDC with 6 decimals)
    mint = await createMint(
      provider.connection,
      (owner as any).payer,
      owner.publicKey,
      null,
      6
    );

    // Derive vault PDA
    [vaultPda, vaultBump] = PublicKey.findProgramAddressSync(
      [VAULT_SEED, mint.toBuffer(), owner.publicKey.toBuffer()],
      program.programId
    );

    // Derive share mint PDA
    [shareMintPda, shareMintBump] = PublicKey.findProgramAddressSync(
      [SHARE_MINT_SEED, vaultPda.toBuffer()],
      program.programId
    );

    // Derive vault token account PDA
    [vaultTokenPda, vaultTokenBump] = PublicKey.findProgramAddressSync(
      [VAULT_TOKEN_SEED, vaultPda.toBuffer()],
      program.programId
    );
  });

  describe("initialize_vault", () => {
    it("should create vault state (step 1)", async () => {
      await program.methods
        .createVault({
          depositCap: new anchor.BN(1_000_000_000_000), // 1M USDC
          minDeposit: new anchor.BN(1_000_000), // 1 USDC
          managementFeeBps: 200, // 2%
          performanceFeeBps: 2000, // 20%
        })
        .accounts({
          owner: owner.publicKey,
          mint: mint,
          vault: vaultPda,
          systemProgram: SystemProgram.programId,
        })
        .rpc();

      // Fetch vault state after step 1
      const vaultState = await program.account.vaultState.fetch(vaultPda);
      expect(vaultState.owner.toString()).to.equal(owner.publicKey.toString());
      expect(vaultState.mint.toString()).to.equal(mint.toString());
      expect(vaultState.totalAssets.toNumber()).to.equal(0);
      expect(vaultState.totalShares.toNumber()).to.equal(0);
      expect(vaultState.depositCap.toNumber()).to.equal(1_000_000_000_000);
      expect(vaultState.minDeposit.toNumber()).to.equal(1_000_000);
      expect(vaultState.managementFeeBps).to.equal(200);
      expect(vaultState.performanceFeeBps).to.equal(2000);
      expect(vaultState.paused).to.equal(false);
    });

    it("should initialize vault accounts (step 2)", async () => {
      await program.methods
        .initVaultAccounts()
        .accounts({
          owner: owner.publicKey,
          mint: mint,
          vault: vaultPda,
          shareMint: shareMintPda,
          vaultTokenAccount: vaultTokenPda,
          systemProgram: SystemProgram.programId,
          tokenProgram: TOKEN_PROGRAM_ID,
          rent: SYSVAR_RENT_PUBKEY,
        })
        .rpc();

      // Verify bumps were stored
      const vaultState = await program.account.vaultState.fetch(vaultPda);
      expect(vaultState.shareMintBump).to.be.greaterThan(0);
      expect(vaultState.tokenAccountBump).to.be.greaterThan(0);
    });
  });

  describe("deposit", () => {
    before(async () => {
      // Create user token account and mint some tokens
      userTokenAccount = await createAccount(
        provider.connection,
        (owner as any).payer,
        mint,
        owner.publicKey
      );

      // Mint 10,000 USDC to user
      await mintTo(
        provider.connection,
        (owner as any).payer,
        mint,
        userTokenAccount,
        owner.publicKey,
        10_000_000_000 // 10,000 USDC (6 decimals)
      );

      // Create user share token account
      userShareAccount = await createAccount(
        provider.connection,
        (owner as any).payer,
        shareMintPda,
        owner.publicKey
      );
    });

    it("should deposit tokens and receive shares (first deposit 1:1)", async () => {
      const depositAmount = new anchor.BN(1_000_000_000); // 1000 USDC

      await program.methods
        .deposit(depositAmount)
        .accounts({
          user: owner.publicKey,
          vault: vaultPda,
          vaultTokenAccount: vaultTokenPda,
          shareMint: shareMintPda,
          userTokenAccount: userTokenAccount,
          userShareAccount: userShareAccount,
          tokenProgram: TOKEN_PROGRAM_ID,
        })
        .rpc();

      // Verify vault state
      const vaultState = await program.account.vaultState.fetch(vaultPda);
      expect(vaultState.totalAssets.toNumber()).to.equal(1_000_000_000);
      expect(vaultState.totalShares.toNumber()).to.equal(1_000_000_000);

      // Verify user received shares
      const shareAccount = await getAccount(provider.connection, userShareAccount);
      expect(Number(shareAccount.amount)).to.equal(1_000_000_000);

      // Verify vault received tokens
      const vaultToken = await getAccount(provider.connection, vaultTokenPda);
      expect(Number(vaultToken.amount)).to.equal(1_000_000_000);
    });

    it("should reject deposit below minimum", async () => {
      try {
        await program.methods
          .deposit(new anchor.BN(100)) // Below min_deposit of 1_000_000
          .accounts({
            user: owner.publicKey,
            vault: vaultPda,
            vaultTokenAccount: vaultTokenPda,
            shareMint: shareMintPda,
            userTokenAccount: userTokenAccount,
            userShareAccount: userShareAccount,
            tokenProgram: TOKEN_PROGRAM_ID,
          })
          .rpc();
        expect.fail("Should have thrown an error");
      } catch (err: any) {
        expect(err.error.errorCode.code).to.equal("BelowMinDeposit");
      }
    });

    it("should mint proportional shares for second deposit", async () => {
      const depositAmount = new anchor.BN(500_000_000); // 500 USDC

      await program.methods
        .deposit(depositAmount)
        .accounts({
          user: owner.publicKey,
          vault: vaultPda,
          vaultTokenAccount: vaultTokenPda,
          shareMint: shareMintPda,
          userTokenAccount: userTokenAccount,
          userShareAccount: userShareAccount,
          tokenProgram: TOKEN_PROGRAM_ID,
        })
        .rpc();

      const vaultState = await program.account.vaultState.fetch(vaultPda);
      // 1000 + 500 = 1500 USDC
      expect(vaultState.totalAssets.toNumber()).to.equal(1_500_000_000);
      // At 1:1 ratio, shares = 1000 + 500 = 1500
      expect(vaultState.totalShares.toNumber()).to.equal(1_500_000_000);
    });
  });

  describe("withdraw", () => {
    it("should withdraw tokens by burning shares", async () => {
      const sharesToBurn = new anchor.BN(500_000_000); // 500 shares

      const userTokenBefore = await getAccount(provider.connection, userTokenAccount);
      const balanceBefore = Number(userTokenBefore.amount);

      await program.methods
        .withdraw(sharesToBurn)
        .accounts({
          user: owner.publicKey,
          vault: vaultPda,
          vaultTokenAccount: vaultTokenPda,
          shareMint: shareMintPda,
          userTokenAccount: userTokenAccount,
          userShareAccount: userShareAccount,
          tokenProgram: TOKEN_PROGRAM_ID,
        })
        .rpc();

      const vaultState = await program.account.vaultState.fetch(vaultPda);
      expect(vaultState.totalAssets.toNumber()).to.equal(1_000_000_000);
      expect(vaultState.totalShares.toNumber()).to.equal(1_000_000_000);

      // User should have received 500 USDC back
      const userTokenAfter = await getAccount(provider.connection, userTokenAccount);
      expect(Number(userTokenAfter.amount) - balanceBefore).to.equal(500_000_000);
    });

    it("should reject withdrawal with insufficient shares", async () => {
      try {
        await program.methods
          .withdraw(new anchor.BN(999_999_999_999)) // Way more than available
          .accounts({
            user: owner.publicKey,
            vault: vaultPda,
            vaultTokenAccount: vaultTokenPda,
            shareMint: shareMintPda,
            userTokenAccount: userTokenAccount,
            userShareAccount: userShareAccount,
            tokenProgram: TOKEN_PROGRAM_ID,
          })
          .rpc();
        expect.fail("Should have thrown an error");
      } catch (err: any) {
        expect(err.error.errorCode.code).to.equal("InsufficientShares");
      }
    });
  });

  describe("admin operations", () => {
    it("should pause the vault", async () => {
      await program.methods
        .pause()
        .accounts({
          owner: owner.publicKey,
          vault: vaultPda,
        })
        .rpc();

      const vaultState = await program.account.vaultState.fetch(vaultPda);
      expect(vaultState.paused).to.equal(true);
    });

    it("should reject deposits when paused", async () => {
      try {
        await program.methods
          .deposit(new anchor.BN(1_000_000))
          .accounts({
            user: owner.publicKey,
            vault: vaultPda,
            vaultTokenAccount: vaultTokenPda,
            shareMint: shareMintPda,
            userTokenAccount: userTokenAccount,
            userShareAccount: userShareAccount,
            tokenProgram: TOKEN_PROGRAM_ID,
          })
          .rpc();
        expect.fail("Should have thrown an error");
      } catch (err: any) {
        expect(err.error.errorCode.code).to.equal("VaultPaused");
      }
    });

    it("should unpause the vault", async () => {
      await program.methods
        .unpause()
        .accounts({
          owner: owner.publicKey,
          vault: vaultPda,
        })
        .rpc();

      const vaultState = await program.account.vaultState.fetch(vaultPda);
      expect(vaultState.paused).to.equal(false);
    });

    it("should add a manager", async () => {
      const manager = Keypair.generate();

      await program.methods
        .addManager(manager.publicKey)
        .accounts({
          owner: owner.publicKey,
          vault: vaultPda,
        })
        .rpc();

      const vaultState = await program.account.vaultState.fetch(vaultPda);
      expect(vaultState.managerCount).to.equal(1);
      expect(vaultState.managers[0].toString()).to.equal(
        manager.publicKey.toString()
      );
    });

    it("should update config", async () => {
      await program.methods
        .updateConfig({
          depositCap: new anchor.BN(5_000_000_000_000),
          minDeposit: new anchor.BN(500_000),
          managementFeeBps: 100,
          performanceFeeBps: 1500,
        })
        .accounts({
          owner: owner.publicKey,
          vault: vaultPda,
        })
        .rpc();

      const vaultState = await program.account.vaultState.fetch(vaultPda);
      expect(vaultState.depositCap.toNumber()).to.equal(5_000_000_000_000);
      expect(vaultState.minDeposit.toNumber()).to.equal(500_000);
      expect(vaultState.managementFeeBps).to.equal(100);
      expect(vaultState.performanceFeeBps).to.equal(1500);
    });

    it("should reject non-owner admin operations", async () => {
      const attacker = Keypair.generate();

      // Airdrop SOL to attacker
      const sig = await provider.connection.requestAirdrop(
        attacker.publicKey,
        1_000_000_000
      );
      await provider.connection.confirmTransaction(sig);

      try {
        await program.methods
          .pause()
          .accounts({
            owner: attacker.publicKey,
            vault: vaultPda,
          })
          .signers([attacker])
          .rpc();
        expect.fail("Should have thrown an error");
      } catch (err: any) {
        // Should fail due to has_one = owner constraint
        expect(err).to.exist;
      }
    });
  });

  describe("update_nav", () => {
    it("should allow manager to update NAV", async () => {
      const vaultStateBefore = await program.account.vaultState.fetch(vaultPda);
      const manager = Keypair.generate();

      // First add this specific manager
      await program.methods
        .addManager(manager.publicKey)
        .accounts({
          owner: owner.publicKey,
          vault: vaultPda,
        })
        .rpc();

      // Airdrop SOL to manager for tx fees
      const sig = await provider.connection.requestAirdrop(
        manager.publicKey,
        1_000_000_000
      );
      await provider.connection.confirmTransaction(sig);

      // Manager updates NAV to simulate yield (10% gain)
      const newNav = new anchor.BN(1_100_000_000); // 1100 USDC (was 1000)

      await program.methods
        .updateNav(newNav)
        .accounts({
          authority: manager.publicKey,
          vault: vaultPda,
        })
        .signers([manager])
        .rpc();

      const vaultState = await program.account.vaultState.fetch(vaultPda);
      expect(vaultState.totalAssets.toNumber()).to.equal(1_100_000_000);
    });

    it("should reject NAV update from unauthorized account", async () => {
      const unauthorized = Keypair.generate();
      const sig = await provider.connection.requestAirdrop(
        unauthorized.publicKey,
        1_000_000_000
      );
      await provider.connection.confirmTransaction(sig);

      try {
        await program.methods
          .updateNav(new anchor.BN(999_999_999))
          .accounts({
            authority: unauthorized.publicKey,
            vault: vaultPda,
          })
          .signers([unauthorized])
          .rpc();
        expect.fail("Should have thrown an error");
      } catch (err: any) {
        expect(err.error.errorCode.code).to.equal("Unauthorized");
      }
    });
  });
});
