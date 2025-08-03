const { ethers } = require("hardhat");

async function main() {
  console.log("🚀 Déploiement du contrat MedicalProcedure...");

  // Récupérer le signer
  const [deployer] = await ethers.getSigners();
  console.log("📝 Déploiement avec l'adresse:", deployer.address);
  console.log("💰 Balance du compte:", (await deployer.getBalance()).toString());

  // Déployer le contrat
  const MedicalProcedure = await ethers.getContractFactory("MedicalProcedure");
  const medicalProcedure = await MedicalProcedure.deploy();
  await medicalProcedure.deployed();

  console.log("✅ Contrat MedicalProcedure déployé à l'adresse:", medicalProcedure.address);

  // Vérifier les rôles
  const adminRole = await medicalProcedure.DEFAULT_ADMIN_ROLE();
  const practitionerRole = await medicalProcedure.PRACTITIONER_ROLE();
  
  console.log("🔐 Rôles configurés:");
  console.log("   - Admin Role:", adminRole);
  console.log("   - Practitioner Role:", practitionerRole);

  // Vérifier que le déployeur a les rôles
  const isAdmin = await medicalProcedure.hasRole(adminRole, deployer.address);
  const isPractitioner = await medicalProcedure.hasRole(practitionerRole, deployer.address);
  
  console.log("👤 Permissions du déployeur:");
  console.log("   - Admin:", isAdmin);
  console.log("   - Practitioner:", isPractitioner);

  // Configuration pour le backend
  console.log("\n📋 Configuration pour le backend:");
  console.log("CONTRACT_ADDRESS=" + medicalProcedure.address);
  console.log("NETWORK_ID=" + (await ethers.provider.getNetwork()).chainId);
  console.log("DEPLOYER_ADDRESS=" + deployer.address);

  // Sauvegarder l'adresse du contrat
  const fs = require("fs");
  const deploymentInfo = {
    contractAddress: medicalProcedure.address,
    networkId: (await ethers.provider.getNetwork()).chainId,
    deployerAddress: deployer.address,
    deploymentTime: new Date().toISOString(),
    adminRole: adminRole,
    practitionerRole: practitionerRole
  };

  fs.writeFileSync(
    "deployment.json",
    JSON.stringify(deploymentInfo, null, 2)
  );

  console.log("\n💾 Informations de déploiement sauvegardées dans deployment.json");

  return medicalProcedure;
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Erreur lors du déploiement:", error);
    process.exit(1);
  });