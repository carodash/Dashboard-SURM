import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SourcingForm = ({ onSubmit, initialData = null, onCancel }) => {
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
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
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
              <input
                type="text"
                name="domaine_activite"
                value={formData.domaine_activite}
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

const DealflowForm = ({ onSubmit, initialData = null, onCancel }) => {
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
    ...initialData
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
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

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [sourcingPartners, setSourcingPartners] = useState([]);
  const [dealflowPartners, setDealflowPartners] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [showSourcingForm, setShowSourcingForm] = useState(false);
  const [showDealflowForm, setShowDealflowForm] = useState(false);
  const [editingPartner, setEditingPartner] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchSourcingPartners = async () => {
    try {
      const response = await axios.get(`${API}/sourcing`);
      setSourcingPartners(response.data);
    } catch (error) {
      console.error("Error fetching sourcing partners:", error);
    }
  };

  const fetchDealflowPartners = async () => {
    try {
      const response = await axios.get(`${API}/dealflow`);
      setDealflowPartners(response.data);
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

  useEffect(() => {
    fetchSourcingPartners();
    fetchDealflowPartners();
    fetchStatistics();
  }, []);

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
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">Partenaires Sourcing</h2>
              <button
                onClick={() => setShowSourcingForm(true)}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
              >
                Nouveau Partenaire
              </button>
            </div>
            
            <div className="bg-white shadow rounded-lg overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Entreprise
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Statut
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Domaine
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Pilote
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {sourcingPartners.map((partner) => (
                    <tr key={partner.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {partner.nom_entreprise}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <span className={`px-2 py-1 rounded-full text-xs ${
                          partner.statut === "A traiter" ? "bg-yellow-100 text-yellow-800" :
                          partner.statut === "Clos" ? "bg-red-100 text-red-800" :
                          partner.statut === "Dealflow" ? "bg-green-100 text-green-800" :
                          "bg-blue-100 text-blue-800"
                        }`}>
                          {partner.statut}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {partner.domaine_activite}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {partner.pilote}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                        <button
                          onClick={() => {
                            setEditingPartner(partner);
                            setShowSourcingForm(true);
                          }}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          Modifier
                        </button>
                        <button
                          onClick={() => handleDeleteSourcing(partner.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          Supprimer
                        </button>
                        {partner.statut !== "Dealflow" && (
                          <button
                            onClick={() => handleTransitionToDealflow(partner.id)}
                            className="text-green-600 hover:text-green-900"
                          >
                            → Dealflow
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === "dealflow" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">Partenaires Dealflow</h2>
              <button
                onClick={() => setShowDealflowForm(true)}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
              >
                Nouveau Partenaire
              </button>
            </div>
            
            <div className="bg-white shadow rounded-lg overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Nom
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Statut
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Domaine
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Métiers
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {dealflowPartners.map((partner) => (
                    <tr key={partner.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {partner.nom}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <span className={`px-2 py-1 rounded-full text-xs ${
                          partner.statut === "Clos" ? "bg-red-100 text-red-800" :
                          partner.statut === "En cours avec les métiers" ? "bg-blue-100 text-blue-800" :
                          "bg-green-100 text-green-800"
                        }`}>
                          {partner.statut}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {partner.domaine}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {partner.metiers_concernes}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                        <button
                          onClick={() => {
                            setEditingPartner(partner);
                            setShowDealflowForm(true);
                          }}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          Modifier
                        </button>
                        <button
                          onClick={() => handleDeleteDealflow(partner.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          Supprimer
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {showSourcingForm && (
        <SourcingForm
          onSubmit={editingPartner ? handleEditSourcing : handleCreateSourcing}
          initialData={editingPartner}
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
          onCancel={() => {
            setShowDealflowForm(false);
            setEditingPartner(null);
          }}
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