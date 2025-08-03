from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
import os
from typing import Optional, Dict, Any
import hashlib

# Configuration Web3
web3 = None
contract = None
contract_address = None

def init_web3():
    """Initialise la connexion Web3 et le contrat"""
    global web3, contract, contract_address
    
    # Configuration réseau
    network_url = os.getenv("BLOCKCHAIN_URL", "http://127.0.0.1:8545")
    contract_address = os.getenv("CONTRACT_ADDRESS")
    
    if not contract_address:
        raise ValueError("CONTRACT_ADDRESS non définie dans les variables d'environnement")
    
    # Connexion Web3
    web3 = Web3(Web3.HTTPProvider(network_url))
    
    # Ajouter le middleware pour les réseaux PoA (Hardhat)
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    
    # Vérifier la connexion
    if not web3.is_connected():
        raise ConnectionError("Impossible de se connecter au réseau blockchain")
    
    # Charger l'ABI du contrat
    abi_path = os.path.join(os.path.dirname(__file__), "../../../contracts/artifacts/contracts/MedicalProcedure.sol/MedicalProcedure.json")
    
    try:
        with open(abi_path, 'r') as f:
            contract_json = json.load(f)
            abi = contract_json['abi']
    except FileNotFoundError:
        # ABI de fallback si le fichier n'existe pas
        abi = [
            {
                "inputs": [],
                "stateMutability": "nonpayable",
                "type": "constructor"
            },
            {
                "anonymous": False,
                "inputs": [
                    {
                        "indexed": True,
                        "internalType": "uint256",
                        "name": "procedureId",
                        "type": "uint256"
                    },
                    {
                        "indexed": True,
                        "internalType": "bytes32",
                        "name": "patientId",
                        "type": "bytes32"
                    },
                    {
                        "indexed": True,
                        "internalType": "address",
                        "name": "practitioner",
                        "type": "address"
                    },
                    {
                        "indexed": False,
                        "internalType": "string",
                        "name": "procedureType",
                        "type": "string"
                    },
                    {
                        "indexed": False,
                        "internalType": "uint256",
                        "name": "timestamp",
                        "type": "uint256"
                    }
                ],
                "name": "ProcedureRecorded",
                "type": "event"
            }
        ]
    
    # Créer l'instance du contrat
    contract = web3.eth.contract(address=contract_address, abi=abi)
    
    print(f"✅ Web3 initialisé - Réseau: {network_url}")
    print(f"📋 Contrat déployé à: {contract_address}")

def get_web3() -> Web3:
    """Retourne l'instance Web3"""
    if web3 is None:
        init_web3()
    return web3

def get_contract():
    """Retourne l'instance du contrat"""
    if contract is None:
        init_web3()
    return contract

def hash_patient_data(patient_id: str) -> str:
    """Génère un hash du patient pour la pseudonymisation"""
    return hashlib.sha256(patient_id.encode()).hexdigest()

def hash_consent_file(file_content: bytes) -> str:
    """Génère un hash du fichier de consentement"""
    return hashlib.sha256(file_content).hexdigest()

def record_procedure_on_blockchain(
    patient_hash: str,
    procedure_type: str,
    duration: int,
    consent_hash: str,
    metadata: str,
    private_key: str
) -> Dict[str, Any]:
    """Enregistre un acte sur la blockchain"""
    if contract is None:
        init_web3()
    
    try:
        # Préparer la transaction
        function = contract.functions.recordProcedure(
            patient_hash,
            procedure_type,
            duration,
            consent_hash,
            metadata
        )
        
        # Estimer le gas
        gas_estimate = function.estimate_gas({'from': web3.eth.accounts[0]})
        
        # Construire la transaction
        transaction = function.build_transaction({
            'from': web3.eth.accounts[0],
            'gas': gas_estimate,
            'gasPrice': web3.eth.gas_price,
            'nonce': web3.eth.get_transaction_count(web3.eth.accounts[0])
        })
        
        # Signer et envoyer la transaction
        signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        # Attendre la confirmation
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        
        return {
            "success": True,
            "tx_hash": tx_hash.hex(),
            "block_number": tx_receipt.blockNumber,
            "gas_used": tx_receipt.gasUsed
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def get_procedure_from_blockchain(procedure_id: int) -> Optional[Dict[str, Any]]:
    """Récupère un acte depuis la blockchain"""
    if contract is None:
        init_web3()
    
    try:
        procedure = contract.functions.getProcedure(procedure_id).call()
        
        return {
            "id": procedure[0],
            "patient_id": procedure[1],
            "practitioner": procedure[2],
            "procedure_type": procedure[3],
            "duration": procedure[4],
            "timestamp": procedure[5],
            "consent_hash": procedure[6],
            "is_active": procedure[7],
            "metadata": procedure[8]
        }
        
    except Exception as e:
        print(f"Erreur lors de la récupération de l'acte {procedure_id}: {e}")
        return None

def get_patient_procedures_from_blockchain(patient_hash: str) -> list:
    """Récupère tous les actes d'un patient depuis la blockchain"""
    if contract is None:
        init_web3()
    
    try:
        procedure_ids = contract.functions.getPatientProcedures(patient_hash).call()
        procedures = []
        
        for proc_id in procedure_ids:
            procedure = get_procedure_from_blockchain(proc_id)
            if procedure:
                procedures.append(procedure)
        
        return procedures
        
    except Exception as e:
        print(f"Erreur lors de la récupération des actes du patient {patient_hash}: {e}")
        return []

def get_practitioner_procedures_from_blockchain(practitioner_address: str) -> list:
    """Récupère tous les actes d'un praticien depuis la blockchain"""
    if contract is None:
        init_web3()
    
    try:
        procedure_ids = contract.functions.getPractitionerProcedures(practitioner_address).call()
        procedures = []
        
        for proc_id in procedure_ids:
            procedure = get_procedure_from_blockchain(proc_id)
            if procedure:
                procedures.append(procedure)
        
        return procedures
        
    except Exception as e:
        print(f"Erreur lors de la récupération des actes du praticien {practitioner_address}: {e}")
        return []

def is_practitioner(practitioner_address: str) -> bool:
    """Vérifie si une adresse a le rôle praticien"""
    if contract is None:
        init_web3()
    
    try:
        return contract.functions.isPractitioner(practitioner_address).call()
    except Exception as e:
        print(f"Erreur lors de la vérification du rôle praticien: {e}")
        return False

def get_total_procedures() -> int:
    """Récupère le nombre total d'actes sur la blockchain"""
    if contract is None:
        init_web3()
    
    try:
        return contract.functions.getTotalProcedures().call()
    except Exception as e:
        print(f"Erreur lors de la récupération du nombre total d'actes: {e}")
        return 0