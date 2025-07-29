import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const DOMAINES_ACTIVITE = [
  "CleanTech",
  "ClimateTech", 
  "Conseil",
  "CX Tech",
  "CyberSecurity",
  "Data",
  "DeathTech",
  "DigitalHealth",
  "EdTech",
  "FinTech",
  "GRC Tech",
  "InsurTech",
  "LegalTech",
  "MarTech",
  "Mobility",
  "Pet Tech",
  "PropTech",
  "RegTech",
  "RetailTech",
  "RhTech",
  "SilverEconomy",
  "SmartHome",
  "Tech"
];

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SearchBar = ({ onSearch, placeholder = "Rechercher..." }) => {
  const [searchTerm, setSearchTerm] = useState("");

  const handleSearch = (e) => {
    const value = e.target.value;
    setSearchTerm(value);
    onSearch(value);
  };

  return (
    <div className="relative">
      <input
        type="text"
        placeholder={placeholder}
        value={searchTerm}
        onChange={handleSearch}
        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      />
      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>
    </div>
  );
};

const SortableTableHeader = ({ children, sortKey, currentSort, onSort }) => {
  const handleSort = () => {
    const newDirection = currentSort.key === sortKey && currentSort.direction === 'asc' ? 'desc' : 'asc';
    onSort(sortKey, newDirection);
  };

  const getSortIcon = () => {
    if (currentSort.key !== sortKey) {
      return (
        <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
        </svg>
      );
    }
    
    return currentSort.direction === 'asc' ? (
      <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
      </svg>
    ) : (
      <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4h13M3 8h9m-9 4h9m5-4v12m0 0l-4-4m4 4l4-4" />
      </svg>
    );
  };

  return (
    <th 
      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
      onClick={handleSort}
    >
      <div className="flex items-center space-x-1">
        <span>{children}</span>
        {getSortIcon()}
      </div>
    </th>
  );
};

const SourcingForm = ({ onSubmit, initialData = null, onCancel, customFields = [] }) => {
  const [formData, setFormData] = useState({
    nom_entreprise: "",
    statut: "A traiter",
    pays_origine: "",
    domaine_activite: "",
    typologie: "",
    objet: "",
    cas_usage: "",
    technologie: "",
    source: "",
    date_entree_sourcing: "",
    interet: true,
    date_presentation_metiers: "",
    pilote: "",
    actions_commentaires: "",
    custom_fields: {},
    ...initialData
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    // Convert date strings to proper format
    const processedData = { ...formData };
    if (processedData.date_entree_sourcing) {
      processedData.date_entree_sourcing = processedData.date_entree_sourcing;
    }
    if (processedData.date_presentation_metiers) {
      processedData.date_presentation_metiers = processedData.date_presentation_metiers;
    }
    onSubmit(processedData);
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    if (name.startsWith('custom_')) {
      const customFieldName = name.replace('custom_', '');
      setFormData(prev => ({
        ...prev,
        custom_fields: {
          ...prev.custom_fields,
          [customFieldName]: type === 'checkbox' ? checked : value
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: type === 'checkbox' ? checked : value
      }));
    }
  };

  const renderCustomField = (field) => {
    const fieldName = `custom_${field.name}`;
    const fieldValue = formData.custom_fields[field.name] || '';

    switch (field.type) {
      case 'text':
      case 'email':
      case 'number':
        return (
          <input
            key={field.id}
            type={field.type}
            name={fieldName}
            value={fieldValue}
            onChange={handleChange}
            required={field.required}
            placeholder={field.placeholder}
            className="w-full border rounded-md px-3 py-2"
          />
        );
      case 'textarea':
        return (
          <textarea
            key={field.id}
            name={fieldName}
            value={fieldValue}
            onChange={handleChange}
            required={field.required}
            placeholder={field.placeholder}
            rows="3"
            className="w-full border rounded-md px-3 py-2"
          />
        );
      case 'select':
        return (
          <select
            key={field.id}
            name={fieldName}
            value={fieldValue}
            onChange={handleChange}
            required={field.required}
            className="w-full border rounded-md px-3 py-2"
          >
            <option value="">Sélectionnez...</option>
            {field.options?.map(option => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        );
      case 'checkbox':
        return (
          <input
            key={field.id}
            type="checkbox"
            name={fieldName}
            checked={fieldValue}
            onChange={handleChange}
            className="mr-2"
          />
        );
      case 'date':
        return (
          <input
            key={field.id}
            type="date"
            name={fieldName}
            value={fieldValue}
            onChange={handleChange}
            required={field.required}
            className="w-full border rounded-md px-3 py-2"
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-4">
          {initialData ? "Modifier" : "Nouveau"} Partenaire Sourcing
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Nom entreprise *</label>
              <input
                type="text"
                name="nom_entreprise"
                value={formData.nom_entreprise}
                onChange={handleChange}
                required
                className="w-full border rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Statut *</label>
              <select
                name="statut"
                value={formData.statut}
                onChange={handleChange}
                required
                className="w-full border rounded-md px-3 py-2"
              >
                <option value="A traiter">A traiter</option>
                <option value="Clos">Clos</option>
                <option value="Dealflow">Dealflow</option>
                <option value="Klaxoon">Klaxoon</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Pays d'origine *</label>
              <input
                type="text"
                name="pays_origine"
                value={formData.pays_origine}
                onChange={handleChange}
                required
                className="w-full border rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Domaine d'activité *</label>
              <select
                name="domaine_activite"
                value={formData.domaine_activite}
                onChange={handleChange}
                required
                className="w-full border rounded-md px-3 py-2"
              >
                <option value="">Sélectionnez un domaine...</option>
                {DOMAINES_ACTIVITE.map(domaine => (
                  <option key={domaine} value={domaine}>{domaine}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Typologie *</label>
              <input
                type="text"
                name="typologie"
                value={formData.typologie}
                onChange={handleChange}
                required
                className="w-full border rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Objet *</label>
              <input
                type="text"
                name="objet"
                value={formData.objet}
                onChange={handleChange}
                required
                className="w-full border rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Cas d'usage *</label>
              <input
                type="text"
                name="cas_usage"
                value={formData.cas_usage}
                onChange={handleChange}
                required
                className="w-full border rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Technologie *</label>
              <input
                type="text"
                name="technologie"
                value={formData.technologie}
                onChange={handleChange}
                required
                className="w-full border rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Source *</label>
              <input
                type="text"
                name="source"
                value={formData.source}
                onChange={handleChange}
                required
                className="w-full border rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Date d'entrée sourcing *</label>
              <input
                type="date"
                name="date_entree_sourcing"
                value={formData.date_entree_sourcing}
                onChange={handleChange}
                required
                className="w-full border rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Pilote *</label>
              <input
                type="text"
                name="pilote"
                value={formData.pilote}
                onChange={handleChange}
                required
                className="w-full border rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Date présentation métiers</label>
              <input
                type="date"
                name="date_presentation_metiers"
                value={formData.date_presentation_metiers}
                onChange={handleChange}
                className="w-full border rounded-md px-3 py-2"
              />
            </div>
            
            {/* Custom Fields */}
            {customFields.filter(field => field.visible).map(field => (
              <div key={field.id}>
                <label className="block text-sm font-medium mb-1">
                  {field.label} {field.required && "*"}
                </label>
                {renderCustomField(field)}
              </div>
            ))}
          </div>
          
          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                name="interet"
                checked={formData.interet}
                onChange={handleChange}
                className="mr-2"
              />
              Intérêt
            </label>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Actions/Commentaires</label>
            <textarea
              name="actions_commentaires"
              value={formData.actions_commentaires}
              onChange={handleChange}
              rows="3"
              className="w-full border rounded-md px-3 py-2"
            />
          </div>
          <div className="flex justify-end space-x-2">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 text-gray-600 bg-gray-200 rounded-md hover:bg-gray-300"
            >
              Annuler
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              {initialData ? "Modifier" : "Créer"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const DealflowForm = ({ onSubmit, initialData = null, onCancel, customFields = [] }) => {
  const [formData, setFormData] = useState({
    nom: "",
    statut: "En cours avec l'équipe inno",
    domaine: "",
    typologie: "",
    objet: "",
    source: "",
    pilote: "",
    metiers_concernes: "",
    date_reception_fichier: "",
    date_pre_qualification: "",
    date_presentation_meetup_referents: "",
    date_presentation_metiers: "",
    date_go_metier_etude: "",
    date_go_experimentation: "",
    date_go_generalisation: "",
    date_cloture: "",
    actions_commentaires: "",
    points_etapes_intermediaires: "",
    custom_fields: {},
    ...initialData
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Ensure all required fields are filled
    if (!formData.nom || !formData.domaine || !formData.typologie || !formData.objet || 
        !formData.source || !formData.pilote || !formData.metiers_concernes || 
        !formData.date_reception_fichier) {
      alert("Veuillez remplir tous les champs requis marqués d'un *");
      return;
    }
    
    // Process date fields
    const processedData = { ...formData };
    
    // Convert empty date strings to null
    Object.keys(processedData).forEach(key => {
      if (key.includes('date') && processedData[key] === '') {
        processedData[key] = null;
      }
    });
    
    console.log("Submitting dealflow data:", processedData);
    onSubmit(processedData);
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    if (name.startsWith('custom_')) {
      const customFieldName = name.replace('custom_', '');
      setFormData(prev => ({
        ...prev,
        custom_fields: {
          ...prev.custom_fields,
          [customFieldName]: type === 'checkbox' ? checked : value
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: type === 'checkbox' ? checked : value
      }));
    }
  };

  const renderCustomField = (field) => {
    const fieldName = `custom_${field.name}`;
    const fieldValue = formData.custom_fields[field.name] || '';

    switch (field.type) {
      case 'text':
      case 'email':
      case 'number':
        return (
          <input
            key={field.id}
            type={field.type}
            name={fieldName}
            value={fieldValue}
            onChange={handleChange}
            required={field.required}
            placeholder={field.placeholder}
            className="w-full border rounded-md px-3 py-2"
          />
        );
      case 'textarea':
        return (
          <textarea
            key={field.id}
            name={fieldName}
            value={fieldValue}
            onChange={handleChange}
            required={field.required}
            placeholder={field.placeholder}
            rows="3"
            className="w-full border rounded-md px-3 py-2"
          />
        );
      case 'select':
        return (
          <select
            key={field.id}
            name={fieldName}
            value={fieldValue}
            onChange={handleChange}
            required={field.required}
            className="w-full border rounded-md px-3 py-2"
          >
            <option value="">Sélectionnez...</option>
            {field.options?.map(option => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        );
      case 'checkbox':
        return (
          <input
            key={field.id}
            type="checkbox"
            name={fieldName}
            checked={fieldValue}
            onChange={handleChange}
            className="mr-2"
          />
        );
      case 'date':
        return (
          <input
            key={field.id}
            type="date"
            name={fieldName}
            value={fieldValue}
            onChange={handleChange}
            required={field.required}
            className="w-full border rounded-md px-3 py-2"
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-4">
          {initialData ? "Modifier" : "Nouveau"} Partenaire Dealflow
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Nom *</label>
              <input
                type="text"
                name="nom"
                value={formData.nom}
                onChange={handleChange}
                required
                className="w-full border rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Statut *</label>
              <select
                name="statut"
                value={formData.statut}
                onChange={handleChange}
                required
                className="w-full border rounded-md px-3 py-2"
              >
                <option value="Clos">Clos</option>
                <option value="En cours avec les métiers">En cours avec les métiers</option>
                <option value="En cours avec l'équipe inno">En cours avec l'équipe inno</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Domaine *</label>
              <input
                type="text"
                name="domaine"
                value={formData.domaine}
                onChange={handleChange}
                required
                className="w-full border rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Typologie *</label>
              <input
                type="text"
                name="typologie"
                value={formData.typologie}
                onChange={handleChange}
                required
                className="w-full border rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Objet *</label>
              <input
                type="text"
                name="objet"
                value={formData.objet}
                onChange={handleChange}
                required
                className="w-full border rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Source *</label>
              <input
                type="text"
                name="source"
                value={formData.source}
                onChange={handleChange}
                required
                className="w-full border rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Pilote *</label>
              <input
                type="text"
                name="pilote"
                value={formData.pilote}
                onChange={handleChange}
                required
                className="w-full border rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Métiers concernés *</label>
              <input
                type="text"
                name="metiers_concernes"
                value={formData.metiers_concernes}
                onChange={handleChange}
                required
                className="w-full border rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Date réception fichier *</label>
              <input
                type="date"
                name="date_reception_fichier"
                value={formData.date_reception_fichier}
                onChange={handleChange}
                required
                className="w-full border rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Date pré-qualification</label>
              <input
                type="date"
                name="date_pre_qualification"
                value={formData.date_pre_qualification}
                onChange={handleChange}
                className="w-full border rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Date présentation meetup référents</label>
              <input
                type="date"
                name="date_presentation_meetup_referents"
                value={formData.date_presentation_meetup_referents}
                onChange={handleChange}
                className="w-full border rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Date présentation métiers</label>
              <input
                type="date"
                name="date_presentation_metiers"
                value={formData.date_presentation_metiers}
                onChange={handleChange}
                className="w-full border rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Date Go métier étude</label>
              <input
                type="date"
                name="date_go_metier_etude"
                value={formData.date_go_metier_etude}
                onChange={handleChange}
                className="w-full border rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Date Go expérimentation</label>
              <input
                type="date"
                name="date_go_experimentation"
                value={formData.date_go_experimentation}
                onChange={handleChange}
                className="w-full border rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Date Go généralisation</label>
              <input
                type="date"
                name="date_go_generalisation"
                value={formData.date_go_generalisation}
                onChange={handleChange}
                className="w-full border rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Date clôture</label>
              <input
                type="date"
                name="date_cloture"
                value={formData.date_cloture}
                onChange={handleChange}
                className="w-full border rounded-md px-3 py-2"
              />
            </div>
            
            {/* Custom Fields */}
            {customFields.filter(field => field.visible).map(field => (
              <div key={field.id}>
                <label className="block text-sm font-medium mb-1">
                  {field.label} {field.required && "*"}
                </label>
                {renderCustomField(field)}
              </div>
            ))}
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Actions/Commentaires</label>
            <textarea
              name="actions_commentaires"
              value={formData.actions_commentaires}
              onChange={handleChange}
              rows="3"
              className="w-full border rounded-md px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Points d'étapes intermédiaires</label>
            <textarea
              name="points_etapes_intermediaires"
              value={formData.points_etapes_intermediaires}
              onChange={handleChange}
              rows="3"
              className="w-full border rounded-md px-3 py-2"
            />
          </div>
          <div className="flex justify-end space-x-2">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 text-gray-600 bg-gray-200 rounded-md hover:bg-gray-300"
            >
              Annuler
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              {initialData ? "Modifier" : "Créer"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const SettingsModal = ({ isOpen, onClose, onSave }) => {
  const [activeTab, setActiveTab] = useState("forms");
  const [formConfig, setFormConfig] = useState({
    sourcing: { fields: [] },
    dealflow: { fields: [] }
  });
  const [columnConfig, setColumnConfig] = useState({
    sourcing: {
      nom_entreprise: { visible: true, label: "Entreprise" },
      statut: { visible: true, label: "Statut" },
      domaine_activite: { visible: true, label: "Domaine" },
      pilote: { visible: true, label: "Pilote" },
      pays_origine: { visible: false, label: "Pays" },
      typologie: { visible: false, label: "Typologie" },
      technologie: { visible: false, label: "Technologie" },
      source: { visible: false, label: "Source" },
      date_entree_sourcing: { visible: false, label: "Date entrée" },
      interet: { visible: false, label: "Intérêt" }
    },
    dealflow: {
      nom: { visible: true, label: "Nom" },
      statut: { visible: true, label: "Statut" },
      domaine: { visible: true, label: "Domaine" },
      metiers_concernes: { visible: true, label: "Métiers" },
      pilote: { visible: false, label: "Pilote" },
      typologie: { visible: false, label: "Typologie" },
      source: { visible: false, label: "Source" },
      date_reception_fichier: { visible: false, label: "Date réception" },
      date_pre_qualification: { visible: false, label: "Date pré-qualification" }
    }
  });
  const [permissions, setPermissions] = useState({
    role: "user",
    permissions: {}
  });
  const [enrichmentSettings, setEnrichmentSettings] = useState({
    auto_enrich: true,
    sources: ["linkedin", "website"]
  });
  const [newField, setNewField] = useState({
    name: "",
    label: "",
    type: "text",
    required: false,
    visible: true
  });

  useEffect(() => {
    if (isOpen) {
      loadSettings();
    }
  }, [isOpen]);

  const loadSettings = async () => {
    try {
      // Load form configurations
      const sourcingConfig = await axios.get(`${API}/config/form/sourcing`);
      const dealflowConfig = await axios.get(`${API}/config/form/dealflow`);
      setFormConfig({
        sourcing: sourcingConfig.data,
        dealflow: dealflowConfig.data
      });

      // Load column configurations
      const columnConfigResponse = await axios.get(`${API}/config/columns`);
      if (columnConfigResponse.data) {
        setColumnConfig(columnConfigResponse.data);
      }
    } catch (error) {
      console.log("No existing config found, using defaults");
    }
  };

  const handleAddField = (formType) => {
    if (!newField.name || !newField.label) return;
    
    const field = {
      ...newField,
      id: `field_${Date.now()}`,
      order: formConfig[formType].fields.length
    };
    
    setFormConfig(prev => ({
      ...prev,
      [formType]: {
        ...prev[formType],
        fields: [...(prev[formType].fields || []), field]
      }
    }));
    
    setNewField({
      name: "",
      label: "",
      type: "text",
      required: false,
      visible: true
    });
  };

  const handleRemoveField = (formType, fieldId) => {
    setFormConfig(prev => ({
      ...prev,
      [formType]: {
        ...prev[formType],
        fields: prev[formType].fields.filter(f => f.id !== fieldId)
      }
    }));
  };

  const handleFieldUpdate = (formType, fieldId, updates) => {
    setFormConfig(prev => ({
      ...prev,
      [formType]: {
        ...prev[formType],
        fields: prev[formType].fields.map(f => 
          f.id === fieldId ? { ...f, ...updates } : f
        )
      }
    }));
  };

  const handleColumnToggle = (formType, columnKey) => {
    setColumnConfig(prev => ({
      ...prev,
      [formType]: {
        ...prev[formType],
        [columnKey]: {
          ...prev[formType][columnKey],
          visible: !prev[formType][columnKey].visible
        }
      }
    }));
  };

  const handleSave = async () => {
    try {
      // Save form configurations
      await axios.post(`${API}/config/form`, {
        form_type: "sourcing",
        fields: formConfig.sourcing.fields || []
      });
      
      await axios.post(`${API}/config/form`, {
        form_type: "dealflow",
        fields: formConfig.dealflow.fields || []
      });

      // Save column configurations
      await axios.post(`${API}/config/columns`, columnConfig);
      
      // Save permissions
      await axios.post(`${API}/config/permissions`, {
        user_id: "current_user",
        ...permissions
      });
      
      // Save enrichment settings
      await axios.post(`${API}/config/enrichment`, enrichmentSettings);
      
      onSave();
      onClose();
    } catch (error) {
      console.error("Error saving settings:", error);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-6xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Paramètres du Dashboard</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>

        <div className="flex border-b mb-6">
          <button
            onClick={() => setActiveTab("forms")}
            className={`px-4 py-2 ${activeTab === "forms" ? "border-b-2 border-blue-500 text-blue-600" : "text-gray-600"}`}
          >
            Configuration Formulaires
          </button>
          <button
            onClick={() => setActiveTab("columns")}
            className={`px-4 py-2 ${activeTab === "columns" ? "border-b-2 border-blue-500 text-blue-600" : "text-gray-600"}`}
          >
            Colonnes à afficher
          </button>
          <button
            onClick={() => setActiveTab("permissions")}
            className={`px-4 py-2 ${activeTab === "permissions" ? "border-b-2 border-blue-500 text-blue-600" : "text-gray-600"}`}
          >
            Autorisations
          </button>
          <button
            onClick={() => setActiveTab("enrichment")}
            className={`px-4 py-2 ${activeTab === "enrichment" ? "border-b-2 border-blue-500 text-blue-600" : "text-gray-600"}`}
          >
            Auto-enrichissement
          </button>
        </div>

        {activeTab === "columns" && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold">Configuration des colonnes à afficher</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {/* Sourcing Columns */}
              <div>
                <h4 className="text-md font-medium mb-4">Colonnes Sourcing</h4>
                <div className="space-y-3">
                  {Object.entries(columnConfig.sourcing).map(([key, config]) => (
                    <div key={key} className="flex items-center justify-between p-3 border rounded-lg">
                      <span className="font-medium">{config.label}</span>
                      <label className="flex items-center">
                        <input
                          type="checkbox"
                          checked={config.visible}
                          onChange={() => handleColumnToggle("sourcing", key)}
                          className="mr-2"
                        />
                        Afficher
                      </label>
                    </div>
                  ))}
                </div>
              </div>

              {/* Dealflow Columns */}
              <div>
                <h4 className="text-md font-medium mb-4">Colonnes Dealflow</h4>
                <div className="space-y-3">
                  {Object.entries(columnConfig.dealflow).map(([key, config]) => (
                    <div key={key} className="flex items-center justify-between p-3 border rounded-lg">
                      <span className="font-medium">{config.label}</span>
                      <label className="flex items-center">
                        <input
                          type="checkbox"
                          checked={config.visible}
                          onChange={() => handleColumnToggle("dealflow", key)}
                          className="mr-2"
                        />
                        Afficher
                      </label>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === "forms" && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {/* Sourcing Form Config */}
              <div>
                <h3 className="text-lg font-semibold mb-4">Formulaire Sourcing</h3>
                <div className="space-y-4">
                  <div className="border rounded-lg p-4">
                    <h4 className="font-medium mb-3">Ajouter un champ</h4>
                    <div className="space-y-2">
                      <input
                        type="text"
                        placeholder="Nom du champ"
                        value={newField.name}
                        onChange={(e) => setNewField({...newField, name: e.target.value})}
                        className="w-full border rounded px-3 py-2"
                      />
                      <input
                        type="text"
                        placeholder="Label affiché"
                        value={newField.label}
                        onChange={(e) => setNewField({...newField, label: e.target.value})}
                        className="w-full border rounded px-3 py-2"
                      />
                      <select
                        value={newField.type}
                        onChange={(e) => setNewField({...newField, type: e.target.value})}
                        className="w-full border rounded px-3 py-2"
                      >
                        <option value="text">Texte</option>
                        <option value="date">Date</option>
                        <option value="select">Liste déroulante</option>
                        <option value="checkbox">Case à cocher</option>
                        <option value="textarea">Zone de texte</option>
                        <option value="number">Nombre</option>
                        <option value="email">Email</option>
                      </select>
                      <div className="flex space-x-4">
                        <label className="flex items-center">
                          <input
                            type="checkbox"
                            checked={newField.required}
                            onChange={(e) => setNewField({...newField, required: e.target.checked})}
                            className="mr-2"
                          />
                          Requis
                        </label>
                        <label className="flex items-center">
                          <input
                            type="checkbox"
                            checked={newField.visible}
                            onChange={(e) => setNewField({...newField, visible: e.target.checked})}
                            className="mr-2"
                          />
                          Visible
                        </label>
                      </div>
                      <button
                        onClick={() => handleAddField("sourcing")}
                        className="w-full bg-blue-600 text-white rounded px-4 py-2 hover:bg-blue-700"
                      >
                        Ajouter
                      </button>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <h4 className="font-medium">Champs personnalisés</h4>
                    {formConfig.sourcing.fields?.map(field => (
                      <div key={field.id} className="flex items-center justify-between p-3 border rounded">
                        <div>
                          <span className="font-medium">{field.label}</span>
                          <span className="text-sm text-gray-500 ml-2">({field.type})</span>
                          {field.required && <span className="text-red-500 ml-1">*</span>}
                        </div>
                        <div className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            checked={field.visible}
                            onChange={(e) => handleFieldUpdate("sourcing", field.id, {visible: e.target.checked})}
                            className="mr-2"
                          />
                          <button
                            onClick={() => handleRemoveField("sourcing", field.id)}
                            className="text-red-600 hover:text-red-800"
                          >
                            Supprimer
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Dealflow Form Config */}
              <div>
                <h3 className="text-lg font-semibold mb-4">Formulaire Dealflow</h3>
                <div className="space-y-4">
                  <div className="border rounded-lg p-4">
                    <h4 className="font-medium mb-3">Ajouter un champ</h4>
                    <div className="space-y-2">
                      <input
                        type="text"
                        placeholder="Nom du champ"
                        value={newField.name}
                        onChange={(e) => setNewField({...newField, name: e.target.value})}
                        className="w-full border rounded px-3 py-2"
                      />
                      <input
                        type="text"
                        placeholder="Label affiché"
                        value={newField.label}
                        onChange={(e) => setNewField({...newField, label: e.target.value})}
                        className="w-full border rounded px-3 py-2"
                      />
                      <select
                        value={newField.type}
                        onChange={(e) => setNewField({...newField, type: e.target.value})}
                        className="w-full border rounded px-3 py-2"
                      >
                        <option value="text">Texte</option>
                        <option value="date">Date</option>
                        <option value="select">Liste déroulante</option>
                        <option value="checkbox">Case à cocher</option>
                        <option value="textarea">Zone de texte</option>
                        <option value="number">Nombre</option>
                        <option value="email">Email</option>
                      </select>
                      <div className="flex space-x-4">
                        <label className="flex items-center">
                          <input
                            type="checkbox"
                            checked={newField.required}
                            onChange={(e) => setNewField({...newField, required: e.target.checked})}
                            className="mr-2"
                          />
                          Requis
                        </label>
                        <label className="flex items-center">
                          <input
                            type="checkbox"
                            checked={newField.visible}
                            onChange={(e) => setNewField({...newField, visible: e.target.checked})}
                            className="mr-2"
                          />
                          Visible
                        </label>
                      </div>
                      <button
                        onClick={() => handleAddField("dealflow")}
                        className="w-full bg-blue-600 text-white rounded px-4 py-2 hover:bg-blue-700"
                      >
                        Ajouter
                      </button>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <h4 className="font-medium">Champs personnalisés</h4>
                    {formConfig.dealflow.fields?.map(field => (
                      <div key={field.id} className="flex items-center justify-between p-3 border rounded">
                        <div>
                          <span className="font-medium">{field.label}</span>
                          <span className="text-sm text-gray-500 ml-2">({field.type})</span>
                          {field.required && <span className="text-red-500 ml-1">*</span>}
                        </div>
                        <div className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            checked={field.visible}
                            onChange={(e) => handleFieldUpdate("dealflow", field.id, {visible: e.target.checked})}
                            className="mr-2"
                          />
                          <button
                            onClick={() => handleRemoveField("dealflow", field.id)}
                            className="text-red-600 hover:text-red-800"
                          >
                            Supprimer
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === "permissions" && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold">Gestion des Autorisations</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium mb-3">Rôle utilisateur</h4>
                <select
                  value={permissions.role}
                  onChange={(e) => setPermissions({...permissions, role: e.target.value})}
                  className="w-full border rounded px-3 py-2"
                >
                  <option value="user">Utilisateur</option>
                  <option value="manager">Manager</option>
                  <option value="admin">Administrateur</option>
                </select>
              </div>
              <div>
                <h4 className="font-medium mb-3">Permissions</h4>
                <div className="space-y-2">
                  {[
                    { key: "create_sourcing", label: "Créer sourcing" },
                    { key: "edit_sourcing", label: "Modifier sourcing" },
                    { key: "delete_sourcing", label: "Supprimer sourcing" },
                    { key: "create_dealflow", label: "Créer dealflow" },
                    { key: "edit_dealflow", label: "Modifier dealflow" },
                    { key: "delete_dealflow", label: "Supprimer dealflow" },
                    { key: "view_statistics", label: "Voir statistiques" },
                    { key: "manage_config", label: "Gérer configuration" }
                  ].map(perm => (
                    <label key={perm.key} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={permissions.permissions[perm.key] || false}
                        onChange={(e) => setPermissions({
                          ...permissions,
                          permissions: {
                            ...permissions.permissions,
                            [perm.key]: e.target.checked
                          }
                        })}
                        className="mr-2"
                      />
                      {perm.label}
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === "enrichment" && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold">Auto-enrichissement des données</h3>
            <div className="space-y-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={enrichmentSettings.auto_enrich}
                  onChange={(e) => setEnrichmentSettings({
                    ...enrichmentSettings,
                    auto_enrich: e.target.checked
                  })}
                  className="mr-2"
                />
                Activer l'auto-enrichissement
              </label>
              
              <div>
                <h4 className="font-medium mb-3">Sources d'enrichissement</h4>
                <div className="space-y-2">
                  {[
                    { key: "linkedin", label: "LinkedIn" },
                    { key: "website", label: "Site web de l'entreprise" },
                    { key: "crunchbase", label: "Crunchbase" }
                  ].map(source => (
                    <label key={source.key} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={enrichmentSettings.sources.includes(source.key)}
                        onChange={(e) => {
                          const newSources = e.target.checked
                            ? [...enrichmentSettings.sources, source.key]
                            : enrichmentSettings.sources.filter(s => s !== source.key);
                          setEnrichmentSettings({
                            ...enrichmentSettings,
                            sources: newSources
                          });
                        }}
                        className="mr-2"
                      />
                      {source.label}
                    </label>
                  ))}
                </div>
              </div>
              
              <div className="p-4 bg-blue-50 rounded-lg">
                <h4 className="font-medium mb-2">Données enrichies automatiquement :</h4>
                <ul className="text-sm text-gray-700 space-y-1">
                  <li>• Année de création</li>
                  <li>• Nombre d'employés</li>
                  <li>• Adresses email de contact</li>
                  <li>• Description de l'entreprise</li>
                  <li>• Informations LinkedIn</li>
                </ul>
              </div>
            </div>
          </div>
        )}

        <div className="flex justify-end space-x-2 mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-600 bg-gray-200 rounded-md hover:bg-gray-300"
          >
            Annuler
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Sauvegarder
          </button>
        </div>
      </div>
    </div>
  );
};

const EnrichedDataModal = ({ isOpen, onClose, partner, partnerType }) => {
  if (!isOpen || !partner) return null;

  const enrichedData = partner.enriched_data || {};
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">Informations Enrichies</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ✕
          </button>
        </div>
        
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-blue-600">
            {partnerType === 'sourcing' ? partner.nom_entreprise : partner.nom}
          </h3>
          <p className="text-sm text-gray-600">
            Dernière mise à jour : {enrichedData.enriched_at ? new Date(enrichedData.enriched_at).toLocaleString('fr-FR') : 'Jamais'}
          </p>
        </div>

        {Object.keys(enrichedData).length === 0 ? (
          <div className="text-center py-8">
            <div className="text-gray-400 text-6xl mb-4">📊</div>
            <p className="text-gray-600">Aucune donnée enrichie disponible</p>
            <p className="text-sm text-gray-500 mt-2">
              Cliquez sur "Enrichir" pour récupérer des informations automatiquement
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {/* LinkedIn Information */}
            {(enrichedData.linkedin_title || enrichedData.linkedin_description) && (
              <div className="bg-blue-50 rounded-lg p-4">
                <h4 className="font-semibold text-blue-800 mb-2">🔗 LinkedIn</h4>
                {enrichedData.linkedin_title && (
                  <p className="text-sm"><strong>Titre:</strong> {enrichedData.linkedin_title}</p>
                )}
                {enrichedData.linkedin_description && (
                  <p className="text-sm mt-2"><strong>Description:</strong> {enrichedData.linkedin_description}</p>
                )}
                {enrichedData.linkedin_url && (
                  <a 
                    href={enrichedData.linkedin_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 text-sm underline mt-2 block"
                  >
                    Voir sur LinkedIn →
                  </a>
                )}
              </div>
            )}

            {/* Website Information */}
            {(enrichedData.website_title || enrichedData.website_description) && (
              <div className="bg-green-50 rounded-lg p-4">
                <h4 className="font-semibold text-green-800 mb-2">🌐 Site Web</h4>
                {enrichedData.website_title && (
                  <p className="text-sm"><strong>Titre:</strong> {enrichedData.website_title}</p>
                )}
                {enrichedData.website_description && (
                  <p className="text-sm mt-2"><strong>Description:</strong> {enrichedData.website_description}</p>
                )}
                {enrichedData.website_url && (
                  <a 
                    href={enrichedData.website_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-green-600 hover:text-green-800 text-sm underline mt-2 block"
                  >
                    Visiter le site →
                  </a>
                )}
              </div>
            )}

            {/* Contact Information */}
            {enrichedData.contact_emails && enrichedData.contact_emails.length > 0 && (
              <div className="bg-purple-50 rounded-lg p-4">
                <h4 className="font-semibold text-purple-800 mb-2">📧 Contacts</h4>
                <div className="space-y-1">
                  {enrichedData.contact_emails.map((email, index) => (
                    <p key={index} className="text-sm">
                      <a href={`mailto:${email}`} className="text-purple-600 hover:text-purple-800">
                        {email}
                      </a>
                    </p>
                  ))}
                </div>
              </div>
            )}

            {/* Additional Information */}
            {Object.keys(enrichedData).filter(key => 
              !key.includes('linkedin') && 
              !key.includes('website') && 
              !key.includes('contact_emails') && 
              key !== 'enriched_at'
            ).length > 0 && (
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="font-semibold text-gray-800 mb-2">ℹ️ Informations supplémentaires</h4>
                <div className="space-y-1">
                  {Object.entries(enrichedData).filter(([key]) => 
                    !key.includes('linkedin') && 
                    !key.includes('website') && 
                    !key.includes('contact_emails') && 
                    key !== 'enriched_at'
                  ).map(([key, value]) => (
                    <p key={key} className="text-sm">
                      <strong className="capitalize">{key.replace(/_/g, ' ')}:</strong> {value}
                    </p>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        <div className="mt-6 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
          >
            Fermer
          </button>
        </div>
      </div>
    </div>
  );
};

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [sourcingPartners, setSourcingPartners] = useState([]);
  const [dealflowPartners, setDealflowPartners] = useState([]);
  const [filteredSourcingPartners, setFilteredSourcingPartners] = useState([]);
  const [filteredDealflowPartners, setFilteredDealflowPartners] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [showSourcingForm, setShowSourcingForm] = useState(false);
  const [showDealflowForm, setShowDealflowForm] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [editingPartner, setEditingPartner] = useState(null);
  const [loading, setLoading] = useState(false);
  const [customFields, setCustomFields] = useState({
    sourcing: [],
    dealflow: []
  });
  const [columnConfig, setColumnConfig] = useState({
    sourcing: {
      nom_entreprise: { visible: true, label: "Entreprise" },
      statut: { visible: true, label: "Statut" },
      domaine_activite: { visible: true, label: "Domaine" },
      pilote: { visible: true, label: "Pilote" },
      pays_origine: { visible: false, label: "Pays" },
      typologie: { visible: false, label: "Typologie" },
      technologie: { visible: false, label: "Technologie" },
      source: { visible: false, label: "Source" },
      date_entree_sourcing: { visible: false, label: "Date entrée" },
      interet: { visible: false, label: "Intérêt" }
    },
    dealflow: {
      nom: { visible: true, label: "Nom" },
      statut: { visible: true, label: "Statut" },
      domaine: { visible: true, label: "Domaine" },
      metiers_concernes: { visible: true, label: "Métiers" },
      pilote: { visible: false, label: "Pilote" },
      typologie: { visible: false, label: "Typologie" },
      source: { visible: false, label: "Source" },
      date_reception_fichier: { visible: false, label: "Date réception" },
      date_pre_qualification: { visible: false, label: "Date pré-qualification" }
    }
  });
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });

  const fetchSourcingPartners = async () => {
    try {
      const response = await axios.get(`${API}/sourcing`);
      setSourcingPartners(response.data);
      setFilteredSourcingPartners(response.data);
    } catch (error) {
      console.error("Error fetching sourcing partners:", error);
    }
  };

  const fetchDealflowPartners = async () => {
    try {
      const response = await axios.get(`${API}/dealflow`);
      setDealflowPartners(response.data);
      setFilteredDealflowPartners(response.data);
    } catch (error) {
      console.error("Error fetching dealflow partners:", error);
    }
  };

  const fetchStatistics = async () => {
    try {
      const response = await axios.get(`${API}/statistics`);
      setStatistics(response.data);
    } catch (error) {
      console.error("Error fetching statistics:", error);
    }
  };

  const fetchCustomFields = async () => {
    try {
      const sourcingConfig = await axios.get(`${API}/config/form/sourcing`);
      const dealflowConfig = await axios.get(`${API}/config/form/dealflow`);
      setCustomFields({
        sourcing: sourcingConfig.data.fields || [],
        dealflow: dealflowConfig.data.fields || []
      });
    } catch (error) {
      console.log("No custom fields configuration found");
    }
  };

  const fetchColumnConfig = async () => {
    try {
      const response = await axios.get(`${API}/config/columns`);
      if (response.data) {
        setColumnConfig(response.data);
      }
    } catch (error) {
      console.log("No column configuration found, using defaults");
    }
  };

  useEffect(() => {
    fetchSourcingPartners();
    fetchDealflowPartners();
    fetchStatistics();
    fetchCustomFields();
    fetchColumnConfig();
  }, []);

  const handleSearch = (searchTerm, type) => {
    if (type === 'sourcing') {
      if (!searchTerm) {
        setFilteredSourcingPartners(sourcingPartners);
      } else {
        const filtered = sourcingPartners.filter(partner =>
          Object.values(partner).some(value =>
            value && value.toString().toLowerCase().includes(searchTerm.toLowerCase())
          )
        );
        setFilteredSourcingPartners(filtered);
      }
    } else {
      if (!searchTerm) {
        setFilteredDealflowPartners(dealflowPartners);
      } else {
        const filtered = dealflowPartners.filter(partner =>
          Object.values(partner).some(value =>
            value && value.toString().toLowerCase().includes(searchTerm.toLowerCase())
          )
        );
        setFilteredDealflowPartners(filtered);
      }
    }
  };

  const handleSort = (key, direction) => {
    setSortConfig({ key, direction });
    
    const sortData = (data) => {
      return [...data].sort((a, b) => {
        let aValue = a[key];
        let bValue = b[key];
        
        // Handle null/undefined values
        if (aValue === null || aValue === undefined) aValue = '';
        if (bValue === null || bValue === undefined) bValue = '';
        
        // Convert to strings for comparison
        aValue = aValue.toString().toLowerCase();
        bValue = bValue.toString().toLowerCase();
        
        if (direction === 'asc') {
          return aValue.localeCompare(bValue);
        } else {
          return bValue.localeCompare(aValue);
        }
      });
    };

    if (activeTab === 'sourcing') {
      setFilteredSourcingPartners(sortData(filteredSourcingPartners));
    } else if (activeTab === 'dealflow') {
      setFilteredDealflowPartners(sortData(filteredDealflowPartners));
    }
  };

  const handleCreateSourcing = async (formData) => {
    setLoading(true);
    try {
      await axios.post(`${API}/sourcing`, formData);
      await fetchSourcingPartners();
      await fetchStatistics();
      setShowSourcingForm(false);
    } catch (error) {
      console.error("Error creating sourcing partner:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateDealflow = async (formData) => {
    setLoading(true);
    try {
      await axios.post(`${API}/dealflow`, formData);
      await fetchDealflowPartners();
      await fetchStatistics();
      setShowDealflowForm(false);
    } catch (error) {
      console.error("Error creating dealflow partner:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleEditSourcing = async (formData) => {
    setLoading(true);
    try {
      await axios.put(`${API}/sourcing/${editingPartner.id}`, formData);
      await fetchSourcingPartners();
      await fetchStatistics();
      setEditingPartner(null);
      setShowSourcingForm(false);
    } catch (error) {
      console.error("Error updating sourcing partner:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleEditDealflow = async (formData) => {
    setLoading(true);
    try {
      await axios.put(`${API}/dealflow/${editingPartner.id}`, formData);
      await fetchDealflowPartners();
      await fetchStatistics();
      setEditingPartner(null);
      setShowDealflowForm(false);
    } catch (error) {
      console.error("Error updating dealflow partner:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSourcing = async (id) => {
    if (window.confirm("Êtes-vous sûr de vouloir supprimer ce partenaire ?")) {
      try {
        await axios.delete(`${API}/sourcing/${id}`);
        await fetchSourcingPartners();
        await fetchStatistics();
      } catch (error) {
        console.error("Error deleting sourcing partner:", error);
      }
    }
  };

  const handleDeleteDealflow = async (id) => {
    if (window.confirm("Êtes-vous sûr de vouloir supprimer ce partenaire ?")) {
      try {
        await axios.delete(`${API}/dealflow/${id}`);
        await fetchDealflowPartners();
        await fetchStatistics();
      } catch (error) {
        console.error("Error deleting dealflow partner:", error);
      }
    }
  };

  const handleTransitionToDealflow = async (sourcingId) => {
    const dealflowData = {
      statut: "En cours avec l'équipe inno",
      metiers_concernes: "À définir",
      date_reception_fichier: new Date().toISOString().split('T')[0]
    };

    try {
      await axios.post(`${API}/transition/${sourcingId}`, dealflowData);
      await fetchSourcingPartners();
      await fetchDealflowPartners();
      await fetchStatistics();
      alert("Partenaire transféré avec succès vers le dealflow !");
    } catch (error) {
      console.error("Error transitioning to dealflow:", error);
      alert("Erreur lors du transfert vers le dealflow");
    }
  };

  const handleEnrichData = async (partnerId, partnerType) => {
    setLoading(true);
    try {
      console.log(`Enriching partner ${partnerId} of type ${partnerType}`);
      const response = await axios.post(`${API}/enrich/${partnerId}?partner_type=${partnerType}`);
      console.log("Enrichment response:", response.data);
      
      if (partnerType === "sourcing") {
        await fetchSourcingPartners();
      } else {
        await fetchDealflowPartners();
      }
      
      alert("Données enrichies avec succès !");
    } catch (error) {
      console.error("Error enriching data:", error);
      alert(`Erreur lors de l'enrichissement des données: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const [showEnrichedData, setShowEnrichedData] = useState(false);
  const [selectedPartner, setSelectedPartner] = useState(null);
  const [selectedPartnerType, setSelectedPartnerType] = useState(null);

  const handleSettingsSave = () => {
    fetchCustomFields();
    fetchColumnConfig();
    fetchSourcingPartners();
    fetchDealflowPartners();
    fetchStatistics();
  };

  const handleShowEnrichedData = (partner, partnerType) => {
    setSelectedPartner(partner);
    setSelectedPartnerType(partnerType);
    setShowEnrichedData(true);
  };

  // Update filtered data when original data changes
  useEffect(() => {
    setFilteredSourcingPartners(sourcingPartners);
  }, [sourcingPartners]);

  useEffect(() => {
    setFilteredDealflowPartners(dealflowPartners);
  }, [dealflowPartners]);

  const renderTableCell = (partner, key, config) => {
    const value = partner[key];
    
    if (key === 'statut') {
      const statusColors = {
        "A traiter": "bg-yellow-100 text-yellow-800",
        "Clos": "bg-red-100 text-red-800",
        "Dealflow": "bg-green-100 text-green-800",
        "Klaxoon": "bg-blue-100 text-blue-800",
        "En cours avec les métiers": "bg-blue-100 text-blue-800",
        "En cours avec l'équipe inno": "bg-green-100 text-green-800"
      };
      
      return (
        <span className={`px-2 py-1 rounded-full text-xs ${statusColors[value] || 'bg-gray-100 text-gray-800'}`}>
          {value}
        </span>
      );
    }
    
    if (key === 'interet') {
      return value ? '✓' : '✗';
    }
    
    if (key.includes('date') && value) {
      return new Date(value).toLocaleDateString('fr-FR');
    }
    
    return value || '-';
  };

  const renderStatisticsCard = (title, value, subtitle = null) => (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-2">{title}</h3>
      <p className="text-3xl font-bold text-blue-600">{value}</p>
      {subtitle && <p className="text-sm text-gray-600 mt-1">{subtitle}</p>}
    </div>
  );

  const renderDistributionChart = (title, data) => (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">{title}</h3>
      <div className="space-y-2">
        {Object.entries(data).map(([key, value]) => (
          <div key={key} className="flex justify-between items-center">
            <span className="text-sm text-gray-600">{key}</span>
            <span className="font-semibold text-blue-600">{value}</span>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <h1 className="text-3xl font-bold text-gray-900">SURM Dashboard</h1>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowSettings(true)}
                className="px-4 py-2 text-gray-600 bg-gray-100 rounded-md hover:bg-gray-200"
              >
                ⚙️ Paramètres
              </button>
              <nav className="flex space-x-8">
                <button
                  onClick={() => setActiveTab("dashboard")}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    activeTab === "dashboard"
                      ? "bg-blue-100 text-blue-700"
                      : "text-gray-500 hover:text-gray-700"
                  }`}
                >
                  Dashboard
                </button>
                <button
                  onClick={() => setActiveTab("sourcing")}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    activeTab === "sourcing"
                      ? "bg-blue-100 text-blue-700"
                      : "text-gray-500 hover:text-gray-700"
                  }`}
                >
                  Sourcing
                </button>
                <button
                  onClick={() => setActiveTab("dealflow")}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    activeTab === "dealflow"
                      ? "bg-blue-100 text-blue-700"
                      : "text-gray-500 hover:text-gray-700"
                  }`}
                >
                  Dealflow
                </button>
              </nav>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === "dashboard" && statistics && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {renderStatisticsCard("Total Sourcing", statistics.total_sourcing)}
              {renderStatisticsCard("Total Dealflow", statistics.total_dealflow)}
              {renderStatisticsCard(
                "Entrées ce trimestre",
                statistics.quarterly_entries.reduce((sum, q) => sum + q.total_entries, 0)
              )}
              {renderStatisticsCard(
                "Pré-qualifications ce mois",
                statistics.monthly_stats.reduce((sum, m) => sum + m.pre_qualifications, 0)
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {renderDistributionChart("Répartition par domaine", statistics.domain_distribution)}
              {renderDistributionChart("Répartition par typologie", statistics.typologie_distribution)}
              {renderDistributionChart("Répartition par technologie", statistics.technology_distribution)}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {renderDistributionChart("Statuts Sourcing", statistics.sourcing_status_distribution)}
              {renderDistributionChart("Statuts Dealflow", statistics.dealflow_status_distribution)}
            </div>
          </div>
        )}

        {activeTab === "sourcing" && (
          <div className="space-y-6">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
              <h2 className="text-2xl font-bold text-gray-900">Partenaires Sourcing</h2>
              <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto">
                <div className="w-full sm:w-80">
                  <SearchBar 
                    onSearch={(term) => handleSearch(term, 'sourcing')}
                    placeholder="Rechercher dans sourcing..."
                  />
                </div>
                <button
                  onClick={() => setShowSourcingForm(true)}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 whitespace-nowrap"
                >
                  Nouveau Partenaire
                </button>
              </div>
            </div>
            
            <div className="bg-white shadow rounded-lg overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      {Object.entries(columnConfig.sourcing).map(([key, config]) => 
                        config.visible ? (
                          <SortableTableHeader
                            key={key}
                            sortKey={key}
                            currentSort={sortConfig}
                            onSort={handleSort}
                          >
                            {config.label}
                          </SortableTableHeader>
                        ) : null
                      )}
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredSourcingPartners.map((partner) => (
                      <tr key={partner.id} className="hover:bg-gray-50">
                        {Object.entries(columnConfig.sourcing).map(([key, config]) => 
                          config.visible ? (
                            <td key={key} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {key === 'nom_entreprise' && (
                                <div className="flex items-center">
                                  <span className="font-medium">{partner[key]}</span>
                                  {partner.enriched_data && (
                                    <span className="ml-2 text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                                      Enrichi
                                    </span>
                                  )}
                                </div>
                              )}
                              {key !== 'nom_entreprise' && renderTableCell(partner, key, config)}
                            </td>
                          ) : null
                        )}
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <div className="flex flex-wrap gap-2">
                            <button
                              onClick={() => {
                                setEditingPartner(partner);
                                setShowSourcingForm(true);
                              }}
                              className="text-blue-600 hover:text-blue-900 hover:bg-blue-50 px-2 py-1 rounded"
                            >
                              Modifier
                            </button>
                            <button
                              onClick={() => handleDeleteSourcing(partner.id)}
                              className="text-red-600 hover:text-red-900 hover:bg-red-50 px-2 py-1 rounded"
                            >
                              Supprimer
                            </button>
                            <button
                              onClick={() => handleEnrichData(partner.id, "sourcing")}
                              disabled={loading}
                              className="text-green-600 hover:text-green-900 hover:bg-green-50 px-2 py-1 rounded disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                              {loading ? "Enrichissement..." : "Enrichir"}
                            </button>
                            {partner.enriched_data && Object.keys(partner.enriched_data).length > 0 && (
                              <button
                                onClick={() => handleShowEnrichedData(partner, "sourcing")}
                                className="text-indigo-600 hover:text-indigo-900 hover:bg-indigo-50 px-2 py-1 rounded"
                              >
                                📊 Voir données
                              </button>
                            )}
                            {partner.statut !== "Dealflow" && (
                              <button
                                onClick={() => handleTransitionToDealflow(partner.id)}
                                className="text-purple-600 hover:text-purple-900 hover:bg-purple-50 px-2 py-1 rounded"
                              >
                                → Dealflow
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              {filteredSourcingPartners.length === 0 && (
                <div className="text-center py-12">
                  <p className="text-gray-500">Aucun partenaire sourcing trouvé.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === "dealflow" && (
          <div className="space-y-6">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
              <h2 className="text-2xl font-bold text-gray-900">Partenaires Dealflow</h2>
              <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto">
                <div className="w-full sm:w-80">
                  <SearchBar 
                    onSearch={(term) => handleSearch(term, 'dealflow')}
                    placeholder="Rechercher dans dealflow..."
                  />
                </div>
                <button
                  onClick={() => setShowDealflowForm(true)}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 whitespace-nowrap"
                >
                  Nouveau Partenaire
                </button>
              </div>
            </div>
            
            <div className="bg-white shadow rounded-lg overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      {Object.entries(columnConfig.dealflow).map(([key, config]) => 
                        config.visible ? (
                          <SortableTableHeader
                            key={key}
                            sortKey={key}
                            currentSort={sortConfig}
                            onSort={handleSort}
                          >
                            {config.label}
                          </SortableTableHeader>
                        ) : null
                      )}
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredDealflowPartners.map((partner) => (
                      <tr key={partner.id} className="hover:bg-gray-50">
                        {Object.entries(columnConfig.dealflow).map(([key, config]) => 
                          config.visible ? (
                            <td key={key} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {key === 'nom' && (
                                <div className="flex items-center">
                                  <span className="font-medium">{partner[key]}</span>
                                  {partner.enriched_data && (
                                    <span className="ml-2 text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                                      Enrichi
                                    </span>
                                  )}
                                </div>
                              )}
                              {key !== 'nom' && renderTableCell(partner, key, config)}
                            </td>
                          ) : null
                        )}
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <div className="flex flex-wrap gap-2">
                            <button
                              onClick={() => {
                                setEditingPartner(partner);
                                setShowDealflowForm(true);
                              }}
                              className="text-blue-600 hover:text-blue-900 hover:bg-blue-50 px-2 py-1 rounded"
                            >
                              Modifier
                            </button>
                            <button
                              onClick={() => handleDeleteDealflow(partner.id)}
                              className="text-red-600 hover:text-red-900 hover:bg-red-50 px-2 py-1 rounded"
                            >
                              Supprimer
                            </button>
                            <button
                              onClick={() => handleEnrichData(partner.id, "dealflow")}
                              disabled={loading}
                              className="text-green-600 hover:text-green-900 hover:bg-green-50 px-2 py-1 rounded disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                              {loading ? "Enrichissement..." : "Enrichir"}
                            </button>
                            {partner.enriched_data && Object.keys(partner.enriched_data).length > 0 && (
                              <button
                                onClick={() => handleShowEnrichedData(partner, "dealflow")}
                                className="text-indigo-600 hover:text-indigo-900 hover:bg-indigo-50 px-2 py-1 rounded"
                              >
                                📊 Voir données
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              {filteredDealflowPartners.length === 0 && (
                <div className="text-center py-12">
                  <p className="text-gray-500">Aucun partenaire dealflow trouvé.</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {showSourcingForm && (
        <SourcingForm
          onSubmit={editingPartner ? handleEditSourcing : handleCreateSourcing}
          initialData={editingPartner}
          customFields={customFields.sourcing}
          onCancel={() => {
            setShowSourcingForm(false);
            setEditingPartner(null);
          }}
        />
      )}

      {showDealflowForm && (
        <DealflowForm
          onSubmit={editingPartner ? handleEditDealflow : handleCreateDealflow}
          initialData={editingPartner}
          customFields={customFields.dealflow}
          onCancel={() => {
            setShowDealflowForm(false);
            setEditingPartner(null);
          }}
        />
      )}

      {showSettings && (
        <SettingsModal
          isOpen={showSettings}
          onClose={() => setShowSettings(false)}
          onSave={handleSettingsSave}
        />
      )}

      {showEnrichedData && (
        <EnrichedDataModal
          isOpen={showEnrichedData}
          onClose={() => setShowEnrichedData(false)}
          partner={selectedPartner}
          partnerType={selectedPartnerType}
        />
      )}
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <Dashboard />
    </div>
  );
}

export default App;