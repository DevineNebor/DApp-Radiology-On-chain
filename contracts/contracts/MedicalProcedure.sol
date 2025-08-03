// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title MedicalProcedure
 * @dev Smart contract pour la gestion des actes de radiologie interventionnelle
 * Inspiré d'Avaneer Health avec traçabilité blockchain et conformité FHIR
 */
contract MedicalProcedure is AccessControl, Pausable {
    using Counters for Counters.Counter;

    // Rôles
    bytes32 public constant PRACTITIONER_ROLE = keccak256("PRACTITIONER_ROLE");
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");

    // Compteurs
    Counters.Counter private _procedureIds;
    Counters.Counter private _patientIds;

    // Structures de données
    struct Procedure {
        uint256 id;
        bytes32 patientId;           // Hash du patient (pseudonymisé)
        address practitioner;        // Adresse du praticien
        string procedureType;        // Type d'intervention
        uint256 duration;            // Durée en minutes
        uint256 timestamp;           // Horodatage de l'acte
        bytes32 consentHash;         // Hash du consentement signé
        bool isActive;               // Statut de l'acte
        string metadata;             // Métadonnées JSON (FHIR)
    }

    struct Patient {
        bytes32 id;                  // Hash du patient
        uint256 firstProcedure;      // Premier acte
        uint256 lastProcedure;       // Dernier acte
        uint256 totalProcedures;     // Nombre total d'actes
    }

    // Mappings
    mapping(uint256 => Procedure) public procedures;
    mapping(bytes32 => Patient) public patients;
    mapping(address => uint256[]) public practitionerProcedures;
    mapping(bytes32 => uint256[]) public patientProcedures;

    // Événements
    event ProcedureRecorded(
        uint256 indexed procedureId,
        bytes32 indexed patientId,
        address indexed practitioner,
        string procedureType,
        uint256 timestamp
    );

    event ConsentUpdated(
        uint256 indexed procedureId,
        bytes32 consentHash,
        uint256 timestamp
    );

    event PatientRegistered(
        bytes32 indexed patientId,
        uint256 timestamp
    );

    // Modifiers
    modifier onlyPractitioner() {
        require(hasRole(PRACTITIONER_ROLE, msg.sender), "MedicalProcedure: practitioner role required");
        _;
    }

    modifier onlyAdmin() {
        require(hasRole(ADMIN_ROLE, msg.sender), "MedicalProcedure: admin role required");
        _;
    }

    modifier procedureExists(uint256 procedureId) {
        require(procedures[procedureId].id != 0, "MedicalProcedure: procedure does not exist");
        _;
    }

    /**
     * @dev Constructeur du contrat
     */
    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
        _grantRole(PRACTITIONER_ROLE, msg.sender);
    }

    /**
     * @dev Enregistre un nouvel acte médical
     * @param patientIdHash Hash du patient (pseudonymisé)
     * @param procedureType Type d'intervention
     * @param duration Durée en minutes
     * @param consentHash Hash du consentement signé
     * @param metadata Métadonnées FHIR en JSON
     */
    function recordProcedure(
        bytes32 patientIdHash,
        string memory procedureType,
        uint256 duration,
        bytes32 consentHash,
        string memory metadata
    ) external onlyPractitioner whenNotPaused {
        require(patientIdHash != bytes32(0), "MedicalProcedure: invalid patient ID");
        require(bytes(procedureType).length > 0, "MedicalProcedure: procedure type required");
        require(duration > 0, "MedicalProcedure: duration must be positive");
        require(consentHash != bytes32(0), "MedicalProcedure: consent hash required");

        _procedureIds.increment();
        uint256 procedureId = _procedureIds.current();

        // Créer l'acte
        procedures[procedureId] = Procedure({
            id: procedureId,
            patientId: patientIdHash,
            practitioner: msg.sender,
            procedureType: procedureType,
            duration: duration,
            timestamp: block.timestamp,
            consentHash: consentHash,
            isActive: true,
            metadata: metadata
        });

        // Mettre à jour les données patient
        if (patients[patientIdHash].id == bytes32(0)) {
            // Nouveau patient
            patients[patientIdHash] = Patient({
                id: patientIdHash,
                firstProcedure: procedureId,
                lastProcedure: procedureId,
                totalProcedures: 1
            });
            emit PatientRegistered(patientIdHash, block.timestamp);
        } else {
            // Patient existant
            patients[patientIdHash].lastProcedure = procedureId;
            patients[patientIdHash].totalProcedures++;
        }

        // Mettre à jour les mappings
        practitionerProcedures[msg.sender].push(procedureId);
        patientProcedures[patientIdHash].push(procedureId);

        emit ProcedureRecorded(
            procedureId,
            patientIdHash,
            msg.sender,
            procedureType,
            block.timestamp
        );
    }

    /**
     * @dev Met à jour le hash du consentement pour un acte
     * @param procedureId ID de l'acte
     * @param newConsentHash Nouveau hash du consentement
     */
    function updateConsent(
        uint256 procedureId,
        bytes32 newConsentHash
    ) external onlyPractitioner procedureExists(procedureId) {
        require(newConsentHash != bytes32(0), "MedicalProcedure: invalid consent hash");
        require(
            procedures[procedureId].practitioner == msg.sender,
            "MedicalProcedure: only procedure practitioner can update consent"
        );

        procedures[procedureId].consentHash = newConsentHash;
        emit ConsentUpdated(procedureId, newConsentHash, block.timestamp);
    }

    /**
     * @dev Récupère un acte par son ID
     * @param procedureId ID de l'acte
     * @return Procedure struct complète
     */
    function getProcedure(uint256 procedureId) external view returns (Procedure memory) {
        require(procedures[procedureId].id != 0, "MedicalProcedure: procedure does not exist");
        return procedures[procedureId];
    }

    /**
     * @dev Récupère tous les actes d'un patient
     * @param patientIdHash Hash du patient
     * @return Array des IDs d'actes
     */
    function getPatientProcedures(bytes32 patientIdHash) external view returns (uint256[] memory) {
        return patientProcedures[patientIdHash];
    }

    /**
     * @dev Récupère tous les actes d'un praticien
     * @param practitioner Adresse du praticien
     * @return Array des IDs d'actes
     */
    function getPractitionerProcedures(address practitioner) external view returns (uint256[] memory) {
        return practitionerProcedures[practitioner];
    }

    /**
     * @dev Récupère les informations d'un patient
     * @param patientIdHash Hash du patient
     * @return Patient struct
     */
    function getPatient(bytes32 patientIdHash) external view returns (Patient memory) {
        return patients[patientIdHash];
    }

    /**
     * @dev Compte le nombre total d'actes
     * @return Nombre total d'actes
     */
    function getTotalProcedures() external view returns (uint256) {
        return _procedureIds.current();
    }

    /**
     * @dev Compte le nombre total de patients
     * @return Nombre total de patients
     */
    function getTotalPatients() external view returns (uint256) {
        return _patientIds.current();
    }

    /**
     * @dev Vérifie si un praticien a le rôle requis
     * @param practitioner Adresse du praticien
     * @return bool True si le praticien a le rôle
     */
    function isPractitioner(address practitioner) external view returns (bool) {
        return hasRole(PRACTITIONER_ROLE, practitioner);
    }

    /**
     * @dev Ajoute un nouveau praticien (admin seulement)
     * @param practitioner Adresse du praticien
     */
    function addPractitioner(address practitioner) external onlyAdmin {
        require(practitioner != address(0), "MedicalProcedure: invalid practitioner address");
        _grantRole(PRACTITIONER_ROLE, practitioner);
    }

    /**
     * @dev Retire un praticien (admin seulement)
     * @param practitioner Adresse du praticien
     */
    function removePractitioner(address practitioner) external onlyAdmin {
        require(practitioner != address(0), "MedicalProcedure: invalid practitioner address");
        _revokeRole(PRACTITIONER_ROLE, practitioner);
    }

    /**
     * @dev Met en pause le contrat (admin seulement)
     */
    function pause() external onlyAdmin {
        _pause();
    }

    /**
     * @dev Reprend le contrat (admin seulement)
     */
    function unpause() external onlyAdmin {
        _unpause();
    }

    /**
     * @dev Supprime un acte (admin seulement, pour corrections)
     * @param procedureId ID de l'acte à supprimer
     */
    function deleteProcedure(uint256 procedureId) external onlyAdmin procedureExists(procedureId) {
        procedures[procedureId].isActive = false;
    }
}