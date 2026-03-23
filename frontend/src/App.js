import React, { useState, useEffect, useRef, useMemo } from "react";
import "./App.css";
import axios from "axios";
import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";

// --- BLOC DE STYLE POUR LES VIGNETTES ---
const cardStyles = document.createElement('style');
cardStyles.innerHTML = `
  .startup-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    padding: 20px 0;
  }
.startup-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 18px;
  display: flex;
  flex-direction: column;
  transition: all 0.2s ease;
  cursor: pointer;
  position: relative;
  height: 100%;
  min-height: 250px;
  box-shadow: 0 4px 16px rgba(15, 23, 42, 0.06);
}

.startup-card:hover {
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.12);
  transform: translateY(-4px);
  border-color: #F42B5F;
}
  .card-badge {
    align-self: flex-start;
    font-size: 10px;
    font-weight: bold;
    text-transform: uppercase;
    padding: 2px 8px;
    border-radius: 99px;
    margin-bottom: 12px;
  }
  .line-clamp-3 {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;  
    overflow: hidden;
  }
`;
document.head.appendChild(cardStyles);

// Custom hook for horizontal scrolling with mouse wheel (optimized)
const useHorizontalScroll = () => {
  const ref = useRef();
  
  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const handleWheel = (e) => {
      // Only intercept vertical wheel events, not horizontal ones
      if (Math.abs(e.deltaY) > Math.abs(e.deltaX) && Math.abs(e.deltaY) > 10) {
        e.preventDefault();
        // Use smooth scrolling with requestAnimationFrame for better performance
        const targetScrollLeft = element.scrollLeft + e.deltaY * 0.5; // Reduced multiplier for smoother scroll
        element.scrollTo({
          left: targetScrollLeft,
          behavior: 'auto' // Use auto instead of smooth to avoid conflicts
        });
      }
    };

    // Use passive: false only when necessary, passive: true for performance
    element.addEventListener('wheel', handleWheel, { passive: false });
    
    return () => {
      element.removeEventListener('wheel', handleWheel);
    };
  }, []);

  return ref;
};
import jsPDF from "jspdf";
import "jspdf-autotable";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  ArcElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar, Line, Pie, Doughnut } from "react-chartjs-2";

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  ArcElement,
  PointElement,
  Title,
  Tooltip,
  Legend
);

const PRIORITE_STRATEGIQUE = {
  HAUTE: { label: "Priorité Haute", color: "bg-red-100 text-red-800", icon: "🔥" },
  MOYENNE: { label: "Priorité Moyenne", color: "bg-yellow-100 text-yellow-800", icon: "⭐" },
  BASSE: { label: "Priorité Basse", color: "bg-green-100 text-green-800", icon: "📌" }
};

const SCORE_MATURITE = [
  { value: 1, label: "1 - Très faible", stars: "⭐" },
  { value: 2, label: "2 - Faible", stars: "⭐⭐" },
  { value: 3, label: "3 - Moyen", stars: "⭐⭐⭐" },
  { value: 4, label: "4 - Élevé", stars: "⭐⭐⭐⭐" },
  { value: 5, label: "5 - Très élevé", stars: "⭐⭐⭐⭐⭐" }
];

const USER_ROLES = {
  ADMIN: { 
    label: "Administrateur", 
    permissions: ["create", "read", "update", "delete", "manage_users", "view_all", "export", "import", "manage_config"]
  },
  CONTRIBUTEUR: { 
    label: "Contributeur", 
    permissions: ["create", "read", "update", "delete", "view_own", "export"]
  },
  OBSERVATEUR: { 
    label: "Observateur", 
    permissions: ["read", "view_all"]
  }
};

const FILTER_OPTIONS = {
  statuts_sourcing: ["A traiter", "Clos", "Dealflow", "Klaxoon"],
  statuts_dealflow: ["Clos", "En cours avec les métiers", "En cours avec l'équipe inno"],
  typologies: ["Startup", "PME", "Scale-up", "Corporate", "Autre"],
  pays: ["France", "Allemagne", "États-Unis", "Royaume-Uni", "Espagne", "Italie", "Suisse", "Belgique", "Autre"],
  sources: ["VivaTech", "Salon tech", "Partenariat", "Concours", "LinkedIn", "Recommandation", "Autre"]
};

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
  "Tech",
  "Autre"
];

// Détection automatique de l'environnement
const isPreview = window.location.hostname.includes('preview.emergentagent.com');
const BACKEND_URL = isPreview 
  ? window.location.origin 
  : (process.env.REACT_APP_BACKEND_URL || "http://localhost:8001");

console.log("🔍 BACKEND_URL AUTO-DÉTECTÉE:", BACKEND_URL);
console.log("🔍 Environnement:", isPreview ? "PREVIEW" : "LOCAL");

const API_URL = `${BACKEND_URL}/api`;

const ScoreDisplay = ({ score, type = "maturite" }) => {
  if (!score) return <span className="text-gray-400">-</span>;
  
  if (type === "maturite") {
    const stars = "⭐".repeat(score);
    return (
      <div className="flex items-center space-x-1">
        <span className="text-yellow-500">{stars}</span>
        <span className="text-sm text-gray-600">({score}/5)</span>
      </div>
    );
  } else if (type === "potentiel") {
    const percentage = (score / 10) * 100;
    return (
      <div className="flex items-center space-x-2">
        <div className="w-16 bg-gray-200 rounded-full h-2">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
            style={{ width: `${percentage}%` }}
          ></div>
        </div>
        <span className="text-sm font-medium text-gray-700">{score}/10</span>
      </div>
    );
  }
  
  return <span>{score}</span>;
};

const PriorityTag = ({ priority }) => {
  if (!priority) return null;
  
  const config = PRIORITE_STRATEGIQUE[priority];
  if (!config) return null;
  
  return (
    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
      <span className="mr-1">{config.icon}</span>
      {config.label}
    </span>
  );
};

const StrategicTags = ({ tags }) => {
  if (!tags || tags.length === 0) return null;
  
  return (
    <div className="flex flex-wrap gap-1">
      {tags.map((tag, index) => (
        <span 
          key={index}
          className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-indigo-100 text-indigo-800"
        >
          {tag}
        </span>
      ))}
    </div>
  );
};

// Phase 5 - Duplicate Detection Component
const DuplicateAlert = ({ duplicates, onViewPartner, onCreateAnyway, onCancel }) => {
  if (!duplicates || duplicates.length === 0) return null;

  return (
    <div className="mt-2 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <svg className="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        </div>
        <div className="ml-3 flex-1">
          <h3 className="text-sm font-medium text-yellow-800">
            ⚠️ Des partenaires similaires existent déjà :
          </h3>
          <div className="mt-2 text-sm text-yellow-700">
            <ul className="space-y-2">
              {duplicates.map((duplicate, index) => (
                <li key={index} className="flex items-center justify-between bg-white p-2 rounded border">
                  <div className="flex-1">
                    <span className="font-medium">{duplicate.name}</span>
                    <span className="ml-2 text-xs bg-gray-100 px-2 py-1 rounded">
                      {duplicate.type === 'sourcing' ? 'Sourcing' : 'Dealflow'}
                    </span>
                    <span className="ml-2 text-xs text-gray-500">
                      {duplicate.similarity * 100}% similarité
                    </span>
                  </div>
                  <div className="ml-4">
                    <button
                      onClick={() => onViewPartner(duplicate)}
                      className="text-blue-600 hover:text-blue-800 text-xs underline"
                    >
                      [Voir la fiche]
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          </div>
          <div className="mt-4 flex space-x-3">
            <button
              onClick={onCreateAnyway}
              className="bg-yellow-600 text-white px-4 py-2 rounded text-sm hover:bg-yellow-700"
            >
              Créer quand même
            </button>
            <button
              onClick={onCancel}
              className="bg-gray-500 text-white px-4 py-2 rounded text-sm hover:bg-gray-600"
            >
              Annuler
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Phase 5 - Custom Hook for Duplicate Detection
const useDuplicateDetection = () => {
  const [duplicates, setDuplicates] = useState([]);
  const [isChecking, setIsChecking] = useState(false);
  
  const checkDuplicates = async (name) => {
    if (!name || name.length < 3) {
      setDuplicates([]);
      return;
    }
    
    setIsChecking(true);
    try {
      const response = await axios.get(`${API_URL}/partners/check-duplicate?name=${encodeURIComponent(name)}`);
      setDuplicates(response.data.duplicates || []);
    } catch (error) {
      console.error('Error checking duplicates:', error);
      setDuplicates([]);
    } finally {
      setIsChecking(false);
    }
  };
  
  // Debounced version to avoid too many API calls
  const debouncedCheck = useRef(null);
  
  const checkDuplicatesDebounced = (name) => {
    if (debouncedCheck.current) {
      clearTimeout(debouncedCheck.current);
    }
    
    debouncedCheck.current = setTimeout(() => {
      checkDuplicates(name);
    }, 500); // 500ms delay
  };
  
  return {
    duplicates,
    isChecking,
    checkDuplicates: checkDuplicatesDebounced,
    clearDuplicates: () => setDuplicates([])
  };
};

// Phase 6 - Company Enrichment Hook
const useCompanyEnrichment = () => {
  const [isEnriching, setIsEnriching] = useState(false);
  const [enrichmentError, setEnrichmentError] = useState(null);
  
  const enrichCompany = async (companyName) => {
    if (!companyName || companyName.length < 3) {
      return null;
    }
    
    setIsEnriching(true);
    setEnrichmentError(null);
    
    try {
      console.log(`🔍 ENRICHISSEMENT - Recherche données pour: ${companyName}`);
      
      // Try to extract domain from company name if it looks like a domain
      let domain = companyName.toLowerCase().trim();
      
      // If it doesn't end with a TLD, try to find the company via Abstract API
      const response = await axios.post(`${API_URL}/enrich-company`, {
        query: companyName,
        domain: domain.includes('.') ? domain : null
      });
      
      if (response.data.success && response.data.company_data) {
        console.log('✅ ENRICHISSEMENT RÉUSSI:', response.data.company_data);
        return response.data.company_data;
      } else {
        console.log('❌ ENRICHISSEMENT ÉCHOUÉ:', response.data.error_message);
        setEnrichmentError(response.data.error_message || 'Aucune donnée trouvée');
        return null;
      }
    } catch (error) {
      console.error('❌ ERREUR ENRICHISSEMENT:', error);
      const errorMsg = error.response?.data?.detail || 'Erreur lors de l\'enrichissement';
      setEnrichmentError(errorMsg);
      return null;
    } finally {
      setIsEnriching(false);
    }
  };
  
  return {
    enrichCompany,
    isEnriching,
    enrichmentError,
    clearError: () => setEnrichmentError(null)
  };
};

// Phase 6 - Advanced Column Filter Component (Excel-like)
const ColumnFilter = ({ 
  data, 
  columnKey, 
  columnLabel, 
  activeFilters, 
  onFilterChange,
  onSort 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  
  // Get unique values for this column
  const uniqueValues = useMemo(() => {
    const values = data
      .map(item => {
        const value = item[columnKey];
        if (value === null || value === undefined) return '(Vide)';
        if (typeof value === 'boolean') return value ? 'Oui' : 'Non';
        if (Array.isArray(value)) return value.join(', ');
        return String(value);
      })
      .filter((value, index, self) => self.indexOf(value) === index)
      .sort();
    return values;
  }, [data, columnKey]);

  // Filter values based on search
  const filteredValues = uniqueValues.filter(value =>
    value.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const currentFilters = activeFilters[columnKey] || [];
  const isNothingSelected = currentFilters.includes('__NONE__');
  const allSelected = (currentFilters.length === 0 && !isNothingSelected) || currentFilters.length === uniqueValues.length;

  const handleValueToggle = (value) => {
    let newFilters;
    
    // Special case: if we're in "nothing selected" mode
    if (currentFilters.includes('__NONE__')) {
      // Start fresh with just this value
      newFilters = [value];
    } else if (currentFilters.length === 0) {
      // If no filters are active (all selected), start with all values except the one being deselected
      newFilters = uniqueValues.filter(v => v !== value);
    } else {
      // Normal toggle logic
      if (currentFilters.includes(value)) {
        newFilters = currentFilters.filter(f => f !== value);
        // If we deselected everything, go to "nothing selected" mode
        if (newFilters.length === 0) {
          newFilters = ['__NONE__'];
        }
      } else {
        newFilters = [...currentFilters, value];
      }
    }
    
    // If all values are selected, clear filters (show all)
    if (newFilters.length === uniqueValues.length) {
      newFilters = [];
    }
    
    onFilterChange(columnKey, newFilters);
  };

  const handleSelectAll = () => {
    if (allSelected) {
      // Deselect all by using special marker
      onFilterChange(columnKey, ['__NONE__']);
    } else {
      // Select all by clearing filters
      onFilterChange(columnKey, []);
    }
  };

  const handleSort = (direction) => {
    onSort(columnKey, direction);
    setIsOpen(false);
  };

  const detectColumnType = () => {
    const sampleValue = data.find(item => item[columnKey] !== null && item[columnKey] !== undefined)?.[columnKey];
    if (!sampleValue) return 'text';
    
    // Check if it's a date
    if (typeof sampleValue === 'string' && sampleValue.match(/^\d{4}-\d{2}-\d{2}/)) {
      return 'date';
    }
    
    // Check if it's numeric
    if (typeof sampleValue === 'number' || (typeof sampleValue === 'string' && !isNaN(Number(sampleValue)))) {
      return 'number';
    }
    
    return 'text';
  };

  const columnType = detectColumnType();

  return (
    <div className="relative inline-block">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="ml-1 p-1 hover:bg-gray-200 rounded"
        title={`Filtrer ${columnLabel}`}
      >
        <svg className="w-3 h-3 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M3 3a1 1 0 011-1h12a1 1 0 011 1v3a1 1 0 01-.293.707L12 11.414V15a1 1 0 01-.293.707l-2 2A1 1 0 018 17v-5.586L3.293 6.707A1 1 0 013 6V3z" clipRule="evenodd" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-1 w-64 bg-white border border-gray-300 rounded-md shadow-lg z-50">
          <div className="p-3">
            {/* Sort Options */}
            <div className="mb-3 pb-3 border-b">
              <div className="text-sm font-medium text-gray-700 mb-2">Trier</div>
              <div className="flex space-x-2">
                <button
                  onClick={() => handleSort('asc')}
                  className="flex items-center px-2 py-1 text-xs bg-blue-50 text-blue-700 rounded hover:bg-blue-100"
                >
                  ↑ {columnType === 'date' ? 'Plus ancien' : columnType === 'number' ? 'Croissant' : 'A → Z'}
                </button>
                <button
                  onClick={() => handleSort('desc')}
                  className="flex items-center px-2 py-1 text-xs bg-blue-50 text-blue-700 rounded hover:bg-blue-100"
                >
                  ↓ {columnType === 'date' ? 'Plus récent' : columnType === 'number' ? 'Décroissant' : 'Z → A'}
                </button>
              </div>
            </div>

            {/* Search */}
            <div className="mb-3">
              <input
                type="text"
                placeholder="Rechercher..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
              />
            </div>

            {/* Select All */}
            <div className="mb-2">
              <label className="flex items-center text-sm font-medium">
                <input
                  type="checkbox"
                  checked={allSelected}
                  onChange={handleSelectAll}
                  className="mr-2"
                />
                (Tout sélectionner)
              </label>
            </div>

            {/* Values List */}
            <div className="max-h-48 overflow-y-auto">
              {filteredValues.map((value, index) => (
                <label key={index} className="flex items-center text-sm py-1 hover:bg-gray-50">
                  <input
                    type="checkbox"
                    checked={!isNothingSelected && (currentFilters.length === 0 || currentFilters.includes(value))}
                    onChange={() => handleValueToggle(value)}
                    className="mr-2"
                  />
                  <span className="truncate">{value}</span>
                </label>
              ))}
            </div>

            {/* Actions */}
            <div className="mt-3 pt-3 border-t flex space-x-2">
              <button
                onClick={() => setIsOpen(false)}
                className="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
              >
                OK
              </button>
              <button
                onClick={() => {
                  onFilterChange(columnKey, []);
                  setSearchTerm('');
                  setIsOpen(false);
                }}
                className="px-3 py-1 text-xs text-blue-600 hover:bg-blue-50 rounded"
              >
                Effacer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Phase 6 - Enhanced Table Header Component
const FilterableTableHeader = ({ 
  column, 
  label, 
  data, 
  activeFilters, 
  onFilterChange, 
  onSort,
  sortConfig 
}) => {
  const getSortIcon = () => {
    if (sortConfig?.column === column) {
      return sortConfig.direction === 'asc' ? ' ↑' : ' ↓';
    }
    return '';
  };

  return (
    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
      <div className="flex items-center">
        <span>{label}{getSortIcon()}</span>
        <ColumnFilter
          data={data}
          columnKey={column}
          columnLabel={label}
          activeFilters={activeFilters}
          onFilterChange={onFilterChange}
          onSort={onSort}
        />
      </div>
    </th>
  );
};

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

// Phase 1 - Inactivity Indicator Component
const InactivityIndicator = ({ isInactive, daysSinceUpdate }) => {
  if (!isInactive) return null;
  
  const getIndicatorColor = (days) => {
    if (days >= 180) return "bg-red-500"; // 6+ months
    if (days >= 120) return "bg-orange-500"; // 4+ months
    return "bg-yellow-500"; // 3+ months
  };
  
  return (
    <div className="flex items-center space-x-1" title={`Inactif depuis ${daysSinceUpdate} jours`}>
      <div className={`w-3 h-3 rounded-full ${getIndicatorColor(daysSinceUpdate)} animate-pulse`}></div>
      <span className="text-xs text-gray-500">{daysSinceUpdate}j</span>
    </div>
  );
};

// Phase 1 - Next Action Date Component
const NextActionDate = ({ date, onUpdate, partnerId, partnerType }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [actionDate, setActionDate] = useState(date || "");
  
  const handleSave = async () => {
    try {
      const updateData = { date_prochaine_action: actionDate || null };
      const response = await axios.put(`${API_URL}/${partnerType}/${partnerId}`, updateData);
      onUpdate(response.data);
      setIsEditing(false);
    } catch (error) {
      console.error("Error updating next action date:", error);
    }
  };
  
  const getUrgencyColor = (date) => {
    if (!date) return "text-gray-400";
    const actionDate = new Date(date);
    const today = new Date();
    const diffDays = Math.ceil((actionDate - today) / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) return "text-red-600 font-medium"; // Overdue
    if (diffDays <= 3) return "text-orange-600 font-medium"; // Soon
    if (diffDays <= 7) return "text-yellow-600"; // This week
    return "text-green-600"; // Future
  };
  
  if (isEditing) {
    return (
      <div className="flex items-center space-x-2">
        <input
          type="date"
          value={actionDate}
          onChange={(e) => setActionDate(e.target.value)}
          className="text-xs border rounded px-2 py-1"
        />
        <button onClick={handleSave} className="text-green-600 hover:text-green-800">
          ✓
        </button>
        <button onClick={() => setIsEditing(false)} className="text-gray-600 hover:text-gray-800">
          ✕
        </button>
      </div>
    );
  }
  
  return (
    <div 
      className={`cursor-pointer text-xs ${getUrgencyColor(date)}`}
      onClick={() => setIsEditing(true)}
      title="Cliquer pour modifier"
    >
      {date ? new Date(date).toLocaleDateString('fr-FR') : "📅 Programmer"}
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
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l4-4 4 4m0 6l-4 4-4-4" />
        </svg>
      );
    }
    return currentSort.direction === 'asc' ? (
      <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
      </svg>
    ) : (
      <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
      </svg>
    );
  };

  return (
    <th 
      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-50"
      onClick={handleSort}
    >
      <div className="flex items-center space-x-1">
        <span>{children}</span>
        {getSortIcon()}
      </div>
    </th>
  );
};

// Phase 1 - Activity Timeline Modal Component
const ActivityTimelineModal = ({ isOpen, onClose, partnerId, partnerType, partnerName }) => {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [newActivity, setNewActivity] = useState("");

  useEffect(() => {
    if (isOpen && partnerId) {
      loadActivities();
    }
  }, [isOpen, partnerId]);

  const loadActivities = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/activity/${partnerId}?partner_type=${partnerType}`);
      setActivities(response.data);
    } catch (error) {
      console.error("Error loading activities:", error);
    } finally {
      setLoading(false);
    }
  };

  const addManualActivity = async () => {
    if (!newActivity.trim()) return;
    
    try {
      await axios.post(`${API_URL}/activity/${partnerId}?partner_type=${partnerType}&description=${encodeURIComponent(newActivity)}&user_name=User`);
      setNewActivity("");
      loadActivities(); // Refresh the timeline
    } catch (error) {
      console.error("Error adding activity:", error);
    }
  };

  const getActivityIcon = (activityType) => {
    switch (activityType) {
      case 'created': return '✨';
      case 'updated': return '📝';
      case 'transitioned': return '🔄';
      case 'comment_added': return '💬';
      case 'status_changed': return '🔄';
      case 'enriched': return '🔍';
      default: return '📋';
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Historique des actions - {partnerName}</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ✕
          </button>
        </div>

        {/* Add new activity */}
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="font-medium mb-2">Ajouter une action</h3>
          <div className="flex space-x-2">
            <input
              type="text"
              value={newActivity}
              onChange={(e) => setNewActivity(e.target.value)}
              placeholder="Décrire l'action effectuée..."
              className="flex-1 border rounded px-3 py-2"
              onKeyPress={(e) => e.key === 'Enter' && addManualActivity()}
            />
            <button
              onClick={addManualActivity}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Ajouter
            </button>
          </div>
        </div>

        {/* Activity Timeline */}
        <div className="space-y-4">
          {loading ? (
            <div className="text-center py-8">Chargement de l'historique...</div>
          ) : activities.length === 0 ? (
            <div className="text-center py-8 text-gray-500">Aucune activité enregistrée</div>
          ) : (
            activities.map((activity, index) => (
              <div key={activity.id} className="flex items-start space-x-4 p-4 border-l-4 border-blue-200 bg-gray-50 rounded-r-lg">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-sm">
                    {getActivityIcon(activity.activity_type)}
                  </div>
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <p className="font-medium text-gray-900">{activity.description}</p>
                    <span className="text-xs text-gray-500">{formatDate(activity.created_at)}</span>
                  </div>
                  {activity.user_name && (
                    <p className="text-sm text-gray-600 mt-1">Par: {activity.user_name}</p>
                  )}
                  {activity.details && Object.keys(activity.details).length > 0 && (
                    <div className="mt-2 text-xs text-gray-600">
                      {activity.details.changes && (
                        <div>
                          <strong>Modifications:</strong>
                          <ul className="list-disc list-inside ml-2">
                            {activity.details.changes.map((change, idx) => (
                              <li key={idx}>{change}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {activity.details.manual_entry && (
                        <span className="inline-block bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-xs">
                          Saisie manuelle
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>

        <div className="flex justify-end mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
          >
            Fermer
          </button>
        </div>
      </div>
    </div>
  );
};

// Phase 2 - Chart Components
const MonthlyEvolutionChart = ({ data, title = "Évolution mensuelle des startups" }) => {
  if (!data || !data.monthly_evolution) return null;

  const chartData = {
    labels: data.monthly_evolution.map(([month, _]) => {
      const [year, monthNum] = month.split('-');
      return new Date(year, monthNum - 1).toLocaleDateString('fr-FR', { 
        month: 'short', 
        year: 'numeric' 
      });
    }),
    datasets: [
      {
        label: 'Sourcing créés',
        data: data.monthly_evolution.map(([_, stats]) => stats.sourcing_created),
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
        borderColor: 'rgb(59, 130, 246)',
        borderWidth: 1,
      },
      {
        label: 'Dealflow créés',
        data: data.monthly_evolution.map(([_, stats]) => stats.dealflow_created),
        backgroundColor: 'rgba(16, 185, 129, 0.8)',
        borderColor: 'rgb(16, 185, 129)',
        borderWidth: 1,
      },
      {
        label: 'Transitions',
        data: data.monthly_evolution.map(([_, stats]) => stats.transitions),
        backgroundColor: 'rgba(245, 158, 11, 0.8)',
        borderColor: 'rgb(245, 158, 11)',
        borderWidth: 1,
      },
      {
        label: 'Clôtures',
        data: data.monthly_evolution.map(([_, stats]) => stats.sourcing_closed + stats.dealflow_closed),
        backgroundColor: 'rgba(239, 68, 68, 0.8)',
        borderColor: 'rgb(239, 68, 68)',
        borderWidth: 1,
      }
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: title,
      },
    },
    scales: {
      x: {
        stacked: true,
      },
      y: {
        stacked: true,
        beginAtZero: true,
      },
    },
  };

  return <Bar data={chartData} options={options} />;
};

const DistributionPieChart = ({ data, title, dataKey }) => {
  if (!data || !data[dataKey]) return null;

  const chartData = {
    labels: Object.keys(data[dataKey]),
    datasets: [
      {
        data: Object.values(data[dataKey]),
        backgroundColor: [
          '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
          '#EC4899', '#14B8A6', '#F97316', '#84CC16', '#6366F1',
          '#06B6D4', '#A855F7', '#F43F5E', '#22C55E', '#EAB308'
        ],
        borderWidth: 2,
        borderColor: '#fff',
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'right',
      },
      title: {
        display: true,
        text: title,
      },
    },
  };

  return <Doughnut data={chartData} options={options} />;
};

// Phase 2 - Analytics Dashboard Component  
const AnalyticsDashboard = ({ isVisible }) => {
  const [monthlyData, setMonthlyData] = useState(null);
  const [distributionData, setDistributionData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dateFilter, setDateFilter] = useState({
    start_date: new Date(new Date().getFullYear() - 1, 0, 1).toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0]
  });
  const [filters, setFilters] = useState({
    filter_by: '',
    filter_value: ''
  });

  useEffect(() => {
    if (isVisible) {
      loadAnalyticsData();
    }
  }, [isVisible, dateFilter, filters]);

  const loadAnalyticsData = async () => {
    setLoading(true);
    try {
      // Load monthly evolution
      const monthlyParams = new URLSearchParams(dateFilter);
      const monthlyResponse = await axios.get(`${API_URL}/analytics/monthly-evolution?${monthlyParams}`);
      setMonthlyData(monthlyResponse.data);

      // Load distribution data
      const distributionParams = new URLSearchParams({
        ...dateFilter,
        ...filters
      });
      const distributionResponse = await axios.get(`${API_URL}/analytics/distribution?${distributionParams}`);
      setDistributionData(distributionResponse.data);
    } catch (error) {
      console.error("Error loading analytics:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDateFilterChange = (field, value) => {
    setDateFilter(prev => ({ ...prev, [field]: value }));
  };

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }));
  };

  if (!isVisible) return null;

  return (
    <div className="space-y-6">
      {/* Filter Controls */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">📊 Filtres d'analyse</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Date début</label>
            <input
              type="date"
              value={dateFilter.start_date}
              onChange={(e) => handleDateFilterChange('start_date', e.target.value)}
              className="w-full border rounded-md px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Date fin</label>
            <input
              type="date"
              value={dateFilter.end_date}
              onChange={(e) => handleDateFilterChange('end_date', e.target.value)}
              className="w-full border rounded-md px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Filtrer par</label>
            <select
              value={filters.filter_by}
              onChange={(e) => handleFilterChange('filter_by', e.target.value)}
              className="w-full border rounded-md px-3 py-2"
            >
              <option value="">Aucun filtre</option>
              <option value="domaine">Domaine</option>
              <option value="pilote">Pilote</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Valeur</label>
            <input
              type="text"
              value={filters.filter_value}
              onChange={(e) => handleFilterChange('filter_value', e.target.value)}
              placeholder="Valeur du filtre..."
              className="w-full border rounded-md px-3 py-2"
              disabled={!filters.filter_by}
            />
          </div>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">Chargement des analyses...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Monthly Evolution Chart */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <MonthlyEvolutionChart data={monthlyData} />
          </div>

          {/* Distribution Charts */}
          {distributionData && (
            <>
              <div className="bg-white rounded-lg shadow-md p-6">
                <DistributionPieChart 
                  data={distributionData} 
                  title="Répartition par statut" 
                  dataKey="by_status" 
                />
              </div>
              
              <div className="bg-white rounded-lg shadow-md p-6">
                <DistributionPieChart 
                  data={distributionData} 
                  title="Répartition par domaine" 
                  dataKey="by_domain" 
                />
              </div>
              
              <div className="bg-white rounded-lg shadow-md p-6">
                <DistributionPieChart 
                  data={distributionData} 
                  title="Répartition par typologie" 
                  dataKey="by_typologie" 
                />
              </div>
            </>
          )}
        </div>
      )}

      {/* Summary Stats */}
      {distributionData && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4">📈 Résumé</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {distributionData.summary.total_sourcing}
              </div>
              <div className="text-sm text-gray-600">Sourcing</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {distributionData.summary.total_dealflow}
              </div>
              <div className="text-sm text-gray-600">Dealflow</div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">
                {distributionData.summary.total_partners}
              </div>
              <div className="text-sm text-gray-600">Total</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Phase 3 - Private Comments Component
const PrivateCommentsModal = ({ isOpen, onClose, partnerId, partnerType, partnerName }) => {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState("");
  const [loading, setLoading] = useState(false);
  const [editingComment, setEditingComment] = useState(null);

  useEffect(() => {
    if (isOpen && partnerId) {
      loadComments();
    }
  }, [isOpen, partnerId]);

  const loadComments = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/comments/${partnerId}?partner_type=${partnerType}&user_id=default_user`);
      setComments(response.data);
    } catch (error) {
      console.error("Error loading comments:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddComment = async () => {
    if (!newComment.trim()) return;
    
    try {
      await axios.post(`${API_URL}/comments?user_id=default_user`, {
        partner_id: partnerId,
        partner_type: partnerType,
        comment: newComment
      });
      setNewComment("");
      loadComments(); // Refresh comments
    } catch (error) {
      console.error("Error adding comment:", error);
    }
  };

  const handleEditComment = async (commentId, newText) => {
    try {
      await axios.put(`${API_URL}/comments/${commentId}?user_id=default_user`, {
        comment: newText
      });
      setEditingComment(null);
      loadComments(); // Refresh comments
    } catch (error) {
      console.error("Error editing comment:", error);
    }
  };

  const handleDeleteComment = async (commentId) => {
    if (!window.confirm("Êtes-vous sûr de vouloir supprimer ce commentaire ?")) return;
    
    try {
      await axios.delete(`${API_URL}/comments/${commentId}?user_id=default_user`);
      loadComments(); // Refresh comments
    } catch (error) {
      console.error("Error deleting comment:", error);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">💬 Commentaires privés - {partnerName}</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ✕
          </button>
        </div>

        {/* Add new comment */}
        <div className="mb-6 p-4 bg-blue-50 rounded-lg">
          <h3 className="font-medium mb-2">Ajouter un commentaire privé</h3>
          <div className="space-y-2">
            <textarea
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              placeholder="Votre commentaire privé (visible uniquement par vous et les admins)..."
              className="w-full border rounded px-3 py-2 h-24 resize-none"
            />
            <button
              onClick={handleAddComment}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Ajouter
            </button>
          </div>
        </div>

        {/* Comments List */}
        <div className="space-y-4">
          {loading ? (
            <div className="text-center py-8">Chargement des commentaires...</div>
          ) : comments.length === 0 ? (
            <div className="text-center py-8 text-gray-500">Aucun commentaire privé</div>
          ) : (
            comments.map((comment) => (
              <div key={comment.id} className="p-4 border border-blue-200 rounded-lg bg-blue-50">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      <span className="font-medium text-blue-800">🔒 {comment.user_name}</span>
                      <span className="text-xs text-gray-500 ml-2">{formatDate(comment.created_at)}</span>
                      {comment.updated_at !== comment.created_at && (
                        <span className="text-xs text-gray-500 ml-1">(modifié)</span>
                      )}
                    </div>
                    {editingComment === comment.id ? (
                      <div className="space-y-2">
                        <textarea
                          defaultValue={comment.comment}
                          className="w-full border rounded px-3 py-2 h-20 resize-none"
                          onKeyDown={(e) => {
                            if (e.key === 'Enter' && e.ctrlKey) {
                              handleEditComment(comment.id, e.target.value);
                            }
                          }}
                        />
                        <div className="flex space-x-2">
                          <button
                            onClick={(e) => {
                              const textarea = e.target.parentNode.parentNode.querySelector('textarea');
                              handleEditComment(comment.id, textarea.value);
                            }}
                            className="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700"
                          >
                            Sauvegarder
                          </button>
                          <button
                            onClick={() => setEditingComment(null)}
                            className="px-3 py-1 bg-gray-600 text-white rounded text-sm hover:bg-gray-700"
                          >
                            Annuler
                          </button>
                        </div>
                      </div>
                    ) : (
                      <p className="text-gray-700 whitespace-pre-wrap">{comment.comment}</p>
                    )}
                  </div>
                  {editingComment !== comment.id && (
                    <div className="flex space-x-2 ml-4">
                      <button
                        onClick={() => setEditingComment(comment.id)}
                        className="text-blue-600 hover:text-blue-800 text-sm"
                      >
                        ✏️
                      </button>
                      <button
                        onClick={() => handleDeleteComment(comment.id)}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        🗑️
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>

        <div className="flex justify-end mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
          >
            Fermer
          </button>
        </div>
      </div>
    </div>
  );
};

// Phase 3 - Personal Dashboard Component
const PersonalDashboard = ({ isVisible, currentUser }) => {
  const [myStartups, setMyStartups] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isVisible && currentUser) {
      loadMyStartups();
    }
  }, [isVisible, currentUser]);

  const loadMyStartups = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/my-startups?user_id=${currentUser.id || 'default_user'}`);
      setMyStartups(response.data);
    } catch (error) {
      console.error("Error loading my startups:", error);
    } finally {
      setLoading(false);
    }
  };

  if (!isVisible) return null;

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold mb-4">👨‍💼 Mes Startups</h2>
        <p className="text-gray-600 mb-6">
          Startups dont vous êtes le pilote : {myStartups?.user?.full_name || currentUser?.full_name}
        </p>

        {loading ? (
          <div className="text-center py-8">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-2 text-gray-600">Chargement de vos startups...</p>
          </div>
        ) : myStartups ? (
          <>
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {myStartups.summary.total_sourcing}
                </div>
                <div className="text-sm text-gray-600">Sourcing</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {myStartups.summary.total_dealflow}
                </div>
                <div className="text-sm text-gray-600">Dealflow</div>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {myStartups.summary.total_partners}
                </div>
                <div className="text-sm text-gray-600">Total</div>
              </div>
              <div className="text-center p-4 bg-red-50 rounded-lg">
                <div className="text-2xl font-bold text-red-600">
                  {myStartups.summary.inactive_sourcing + myStartups.summary.inactive_dealflow}
                </div>
                <div className="text-sm text-gray-600">Inactifs (90j+)</div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Recent Sourcing */}
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-semibold text-blue-800 mb-3">📋 Sourcing récents</h3>
                {myStartups.sourcing_partners.slice(0, 5).map(partner => (
                  <div key={partner.id} className="flex justify-between items-center py-2 border-b border-blue-200 last:border-b-0">
                    <div>
                      <span className="font-medium">{partner.nom_entreprise}</span>
                      <span className="text-sm text-gray-600 ml-2">({partner.domaine_activite})</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      {partner.is_inactive && (
                        <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" title="Inactif"></span>
                      )}
                      <span className={`text-xs px-2 py-1 rounded ${
                        partner.statut === 'A traiter' ? 'bg-yellow-100 text-yellow-800' :
                        partner.statut === 'Dealflow' ? 'bg-green-100 text-green-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {partner.statut}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Recent Dealflow */}
              <div className="bg-green-50 p-4 rounded-lg">
                <h3 className="font-semibold text-green-800 mb-3">🚀 Dealflow récents</h3>
                {myStartups.dealflow_partners.slice(0, 5).map(partner => (
                  <div key={partner.id} className="flex justify-between items-center py-2 border-b border-green-200 last:border-b-0">
                    <div>
                      <span className="font-medium">{partner.nom}</span>
                      <span className="text-sm text-gray-600 ml-2">({partner.domaine})</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      {partner.is_inactive && (
                        <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" title="Inactif"></span>
                      )}
                      <span className={`text-xs px-2 py-1 rounded ${
                        partner.statut === 'En cours avec les métiers' ? 'bg-blue-100 text-blue-800' :
                        partner.statut === 'En cours avec l\'équipe inno' ? 'bg-green-100 text-green-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {partner.statut}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        ) : (
          <div className="text-center py-8 text-gray-500">
            Aucune startup assignée
          </div>
        )}
      </div>
    </div>
  );
};

// Phase 4 - Enhanced Table Container with top scrollbar and wheel support
const EnhancedTableContainer = ({ children, tableId, title }) => {
  const horizontalScrollRef = useHorizontalScroll();
  const topScrollRef = useRef();
  const [mainScrollElement, setMainScrollElement] = useState(null);

  useEffect(() => {
    const mainScroll = horizontalScrollRef.current;
    if (mainScroll) {
      setMainScrollElement(mainScroll);
    }
  }, [horizontalScrollRef]);

  useEffect(() => {
    if (!topScrollRef.current || !mainScrollElement) return;

    const handleTopScroll = () => {
      if (mainScrollElement) {
        mainScrollElement.scrollLeft = topScrollRef.current.scrollLeft;
      }
    };

    const handleMainScroll = () => {
      if (topScrollRef.current) {
        topScrollRef.current.scrollLeft = mainScrollElement.scrollLeft;
      }
    };

    topScrollRef.current.addEventListener('scroll', handleTopScroll);
    mainScrollElement.addEventListener('scroll', handleMainScroll);

    return () => {
      if (topScrollRef.current) {
        topScrollRef.current.removeEventListener('scroll', handleTopScroll);
      }
      if (mainScrollElement) {
        mainScrollElement.removeEventListener('scroll', handleMainScroll);
      }
    };
  }, [mainScrollElement]);

  return (
    <div className="bg-white shadow rounded-lg overflow-hidden">
      {/* Top scrollbar for tables */}
      <div className="top-scrollbar-container">
        <div className="flex items-center space-x-3 px-4">
          <span className="text-sm font-medium text-gray-600">📜 {title}</span>
          <div 
            ref={topScrollRef}
            className="top-scrollbar flex-1"
          >
            <div style={{ width: '1200px', height: '1px' }}></div>
          </div>
          <span className="text-xs text-gray-500">Molette pour scroll</span>
        </div>
      </div>
      
      {/* Main table container with wheel support */}
      <div 
        ref={horizontalScrollRef}
        className="enhanced-table-scroll wheel-horizontal-scroll"
      >
        {children}
      </div>
    </div>
  );
};

// Phase 4 - Kanban Card Component
const KanbanCard = ({ partner, index }) => {
  // Debug logging
  console.log(`🔍 DEBUG KanbanCard rendering:`, { 
    kanban_id: partner.kanban_id, 
    index, 
    partner_type: partner.partner_type 
  });
  
  const getCardColor = (partnerType) => {
    return partnerType === 'sourcing' ? 'border-blue-200 bg-blue-50' : 'border-green-200 bg-green-50';
  };

  const getTypeIcon = (partnerType) => {
    return partnerType === 'sourcing' ? '🔍' : '🚀';
  };

  const formatDate = (dateString) => {
    if (!dateString) return null;
    return new Date(dateString).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' });
  };

  const getPartnerName = (partner) => {
    return partner.partner_type === 'sourcing' ? partner.nom_entreprise : partner.nom;
  };

  // Ensure kanban_id is a string
  const draggableId = String(partner.kanban_id);

  return (
    <Draggable draggableId={draggableId} index={index}>
      {(provided, snapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          className={`p-3 mb-2 rounded-lg border-2 shadow-sm cursor-move transition-all ${getCardColor(partner.partner_type)} ${
            snapshot.isDragging ? 'shadow-lg rotate-3 scale-105' : 'hover:shadow-md'
          }`}
        >
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center space-x-2">
              <span className="text-lg">{getTypeIcon(partner.partner_type)}</span>
              <h4 className="font-semibold text-sm text-gray-800 leading-tight">
                {getPartnerName(partner)}
              </h4>
            </div>
            {partner.is_inactive && (
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" title="Inactif 90j+"></div>
            )}
          </div>
          
          <div className="space-y-1 text-xs text-gray-600">
            <div className="flex items-center space-x-1">
              <span>👤</span>
              <span className="truncate">{partner.pilote}</span>
            </div>
            
            <div className="flex items-center space-x-1">
              <span>🏢</span>
              <span className="truncate">{partner.partner_type === 'sourcing' ? partner.domaine_activite : partner.domaine}</span>
            </div>
            
            {partner.date_prochaine_action && (
              <div className="flex items-center space-x-1">
                <span>📅</span>
                <span className={`font-medium ${
                  new Date(partner.date_prochaine_action) < new Date() ? 'text-red-600' : 'text-green-600'
                }`}>
                  {formatDate(partner.date_prochaine_action)}
                </span>
              </div>
            )}
            
            {partner.updated_at && (
              <div className="flex items-center space-x-1 text-gray-500">
                <span>🕒</span>
                <span>MAJ {formatDate(partner.updated_at)}</span>
              </div>
            )}
          </div>
        </div>
      )}
    </Draggable>
  );
};

// Phase 4 - Kanban Top Scrollbar Component (Performance Optimized)
const KanbanTopScrollbar = ({ kanbanData }) => {
  const topScrollRef = useRef();
  const [mainScrollElement, setMainScrollElement] = useState(null);
  const syncInProgress = useRef(false); // Prevent sync loops

  useEffect(() => {
    const mainScroll = document.querySelector('.kanban-main-scroll');
    if (mainScroll) {
      setMainScrollElement(mainScroll);
    }
  }, []);

  useEffect(() => {
    if (!topScrollRef.current || !mainScrollElement) return;

    // Throttled scroll handlers for better performance
    const handleTopScroll = () => {
      if (syncInProgress.current) return;
      syncInProgress.current = true;
      
      requestAnimationFrame(() => {
        if (mainScrollElement && topScrollRef.current) {
          mainScrollElement.scrollLeft = topScrollRef.current.scrollLeft;
        }
        syncInProgress.current = false;
      });
    };

    const handleMainScroll = () => {
      if (syncInProgress.current) return;
      syncInProgress.current = true;
      
      requestAnimationFrame(() => {
        if (topScrollRef.current && mainScrollElement) {
          topScrollRef.current.scrollLeft = mainScrollElement.scrollLeft;
        }
        syncInProgress.current = false;
      });
    };

    const topElement = topScrollRef.current;
    topElement.addEventListener('scroll', handleTopScroll, { passive: true });
    mainScrollElement.addEventListener('scroll', handleMainScroll, { passive: true });

    return () => {
      if (topElement) {
        topElement.removeEventListener('scroll', handleTopScroll);
      }
      if (mainScrollElement) {
        mainScrollElement.removeEventListener('scroll', handleMainScroll);
      }
    };
  }, [mainScrollElement]);

  const totalWidth = kanbanData.columnOrder.length * 20; // Same calculation as main container

  return (
    <div className="top-scrollbar-container mb-4">
      <div className="flex items-center space-x-3 px-2">
        <span className="text-sm font-medium text-gray-600">📜 Scroll horizontal</span>
        <div 
          ref={topScrollRef}
          className="top-scrollbar flex-1"
          style={{ scrollBehavior: 'auto' }} // Disable smooth scrolling for performance
        >
          <div style={{ width: `${totalWidth}rem`, height: '1px' }}></div>
        </div>
        <span className="text-xs text-gray-500">{kanbanData.columnOrder.length} colonnes</span>
      </div>
    </div>
  );
};

// Phase 4 - Kanban Scroll Container with wheel support
const KanbanScrollContainer = ({ kanbanData }) => {
  const horizontalScrollRef = useHorizontalScroll();

  return (
    <div 
      ref={horizontalScrollRef}
      className="enhanced-horizontal-scroll wheel-horizontal-scroll kanban-main-scroll pb-4"
    >
      <div 
        className="flex space-x-4 pb-4 px-2" 
        style={{ 
          minWidth: 'max-content',
          width: `${kanbanData.columnOrder.length * 20}rem`
        }}
      >
        {kanbanData.columnOrder.map(columnId => {
          const column = kanbanData.columns[columnId];
          const partners = column.partners;
          
          return (
            <KanbanColumn
              key={columnId}
              column={column}
              partners={partners}
            />
          );
        })}
      </div>
    </div>
  );
};
const KanbanColumn = ({ column, partners }) => {
  return (
    <div className="bg-gray-100 rounded-lg p-2 min-h-[600px] w-72 flex-shrink-0 lg:w-80">
      <div className="mb-3">
        <h3 className="font-bold text-gray-800 text-xs lg:text-sm truncate" title={column.title}>
          {column.title}
        </h3>
        <p className="text-xs text-gray-600 truncate" title={column.subtitle}>
          {column.subtitle}
        </p>
        <div className="mt-2 bg-white rounded px-2 py-1 text-xs font-medium text-gray-700">
          {partners.length} startup{partners.length !== 1 ? 's' : ''}
        </div>
      </div>
      
      <Droppable droppableId={column.id} isDropDisabled={false}>
        {(provided, snapshot) => (
          <div
            ref={provided.innerRef}
            {...provided.droppableProps}
            className={`min-h-[500px] rounded-lg p-2 transition-colors ${
              snapshot.isDraggingOver ? 'bg-blue-100 border-2 border-blue-300' : 'bg-gray-50'
            }`}
          >
            {partners.map((partner, index) => (
              <KanbanCard key={partner.kanban_id} partner={partner} index={index} />
            ))}
            {provided.placeholder}
          </div>
        )}
      </Droppable>
    </div>
  );
};

// Phase 4 - Kanban Board Component
const KanbanBoard = ({ isVisible }) => {
  const [kanbanData, setKanbanData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isVisible) {
      loadKanbanData();
    }
  }, [isVisible]);

  const loadKanbanData = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/kanban-data?user_id=default_user`);
      console.log('🔍 DEBUG Kanban data received:', response.data);
      
      // Debug first partner in first column
      if (response.data?.columns) {
        const firstColumn = Object.values(response.data.columns)[0];
        if (firstColumn?.partners?.length > 0) {
          console.log('🔍 DEBUG First partner:', firstColumn.partners[0]);
        }
      }
      
      setKanbanData(response.data);
    } catch (error) {
      console.error("Error loading kanban data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDragEnd = async (result) => {
    const { destination, source, draggableId } = result;

    // If dropped outside any droppable
    if (!destination) {
      return;
    }

    // If dropped in the same position
    if (destination.droppableId === source.droppableId && destination.index === source.index) {
      return;
    }

    // Extract partner info from draggableId
    // BUG CORRIGÉ : séparateur | au lieu de _ pour éviter le conflit avec les UUIDs
    const separatorIndex = draggableId.indexOf('|');
    const partnerType = draggableId.substring(0, separatorIndex);
    const partnerId = draggableId.substring(separatorIndex + 1);

    try {
      console.log(`🔄 Moving ${partnerType}_${partnerId} from ${source.droppableId} to ${destination.droppableId}`);
      
      // Fixed: Use query parameters instead of JSON body, and correct parameter name
      const params = new URLSearchParams({
        partner_id: partnerId,
        partner_type: partnerType,
        source_column: source.droppableId,
        destination_column: destination.droppableId, // Fixed: was target_column, now destination_column
        user_id: 'default_user'
      });
      
      console.log('🔍 DEBUGGING DRAG & DROP - Paramètres API:', {
        partner_id: partnerId,
        partner_type: partnerType,
        source_column: source.droppableId,
        destination_column: destination.droppableId,
        api_url: `${API_URL}/kanban-move?${params}`
      });
      
      const response = await axios.post(`${API_URL}/kanban-move?${params}`);

      console.log('✅ Move successful:', response.data);
      console.log('✅ Response status:', response.status);
      console.log('✅ Response headers:', response.headers);
      
      // Show success feedback
      alert(`✅ Startup déplacée avec succès vers "${destination.droppableId}"\nNouveau statut: ${response.data?.new_status || 'N/A'}`);
      
      // Reload data to reflect changes
      loadKanbanData();
      
    } catch (error) {
      console.error("❌ Error moving partner:", error);
      console.error("❌ Error details:", {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        url: error.config?.url
      });
      
      // Show error feedback with details
      let errorMessage = "❌ Erreur lors du déplacement:\n";
      
      if (error.response?.status === 403) {
        errorMessage += "⚠️ Autorisation refusée. Seuls les pilotes et admins peuvent modifier leurs startups.";
      } else if (error.response?.status === 400) {
        const detail = error.response?.data?.detail || "Déplacement invalide";
        errorMessage += `⚠️ Déplacement invalide: ${detail}`;
      } else if (error.response?.status === 404) {
        errorMessage += "⚠️ Startup non trouvée. Actualisez la page.";
      } else if (error.response) {
        errorMessage += `⚠️ Erreur HTTP ${error.response.status}: ${error.response.data?.detail || error.response.statusText}`;
      } else if (error.request) {
        errorMessage += "⚠️ Impossible de contacter le serveur. Vérifiez votre connexion.";
      } else {
        errorMessage += `⚠️ Erreur: ${error.message}`;
      }
      
      alert(errorMessage);
      
      // Reload data to reset any visual changes
      loadKanbanData();
    }
  };

  if (!isVisible) return null;

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h2 className="text-2xl font-bold">📋 Pipeline Kanban</h2>
            <p className="text-gray-600">Vue d'ensemble du cycle de vie des startups</p>
          </div>
          <button
            onClick={loadKanbanData}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            🔄 Actualiser
          </button>
        </div>

        {/* Summary Stats */}
        {kanbanData && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="text-center p-3 bg-blue-50 rounded-lg">
              <div className="text-xl font-bold text-blue-600">{kanbanData.summary.total_sourcing}</div>
              <div className="text-sm text-gray-600">Sourcing</div>
            </div>
            <div className="text-center p-3 bg-green-50 rounded-lg">
              <div className="text-xl font-bold text-green-600">{kanbanData.summary.total_dealflow}</div>
              <div className="text-sm text-gray-600">Dealflow</div>
            </div>
            <div className="text-center p-3 bg-purple-50 rounded-lg">
              <div className="text-xl font-bold text-purple-600">{kanbanData.summary.total_partners}</div>
              <div className="text-sm text-gray-600">Total</div>
            </div>
            <div className="text-center p-3 bg-orange-50 rounded-lg">
              <div className="text-xl font-bold text-orange-600">
                {Object.values(kanbanData.summary.by_column).reduce((sum, count) => sum + count, 0)}
              </div>
              <div className="text-sm text-gray-600">En pipeline</div>
            </div>
          </div>
        )}

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-2 text-gray-600">Chargement du pipeline...</p>
          </div>
        ) : kanbanData ? (
          <DragDropContext onDragEnd={handleDragEnd}>
            {/* Top horizontal scrollbar for better accessibility */}
            <KanbanTopScrollbar kanbanData={kanbanData} />
            
            {/* Enhanced horizontal scroll container with wheel support */}
            <KanbanScrollContainer kanbanData={kanbanData} />
            
            {/* Enhanced scroll hint */}
            <div className="text-center text-xs text-gray-500 mt-2 bg-blue-50 p-3 rounded-lg">
              <div className="flex items-center justify-center space-x-4 flex-wrap gap-2">
                <span>💡 <strong>Glisser-déposer :</strong> Déplacez les cartes entre colonnes</span>
                <span>•</span>
                <span>🖱️ <strong>Molette :</strong> Scroll horizontal en survolant le tableau</span>
                <span>•</span>
                <span>📜 <strong>Barres :</strong> Scroll accessible en haut et en bas</span>
              </div>
            </div>
          </DragDropContext>
        ) : (
          <div className="text-center py-8 text-gray-500">
            Erreur de chargement des données
          </div>
        )}
      </div>
    </div>
  );
};

// Phase 4 - Synthetic Reports Component
const SyntheticReports = ({ isVisible }) => {
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isVisible) {
      loadReportData();
    }
  }, [isVisible]);

  const loadReportData = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/synthetic-report?user_id=default_user`);
      setReportData(response.data);
    } catch (error) {
      console.error("Error loading report data:", error);
    } finally {
      setLoading(false);
    }
  };

  const exportToPDF = () => {
    if (!reportData) return;

    const doc = new jsPDF();
    const currentDate = new Date().toLocaleDateString('fr-FR');
    
    // Title
    doc.setFontSize(20);
    doc.text('RAPPORT SYNTHÉTIQUE SURM', 20, 20);
    doc.setFontSize(12);
    doc.text(`Généré le ${currentDate} par ${reportData.summary.generated_by}`, 20, 30);

    let yPosition = 50;

    // Summary
    doc.setFontSize(16);
    doc.text('RÉSUMÉ EXÉCUTIF', 20, yPosition);
    yPosition += 10;
    
    doc.setFontSize(12);
    doc.text(`Total Startups: ${reportData.summary.total_partners}`, 20, yPosition);
    yPosition += 8;
    doc.text(`Sourcing: ${reportData.summary.total_sourcing} | Dealflow: ${reportData.summary.total_dealflow}`, 20, yPosition);
    yPosition += 15;

    // Cross-table by Status
    doc.setFontSize(14);
    doc.text('RÉPARTITION PAR STATUT', 20, yPosition);
    yPosition += 10;

    const statusData = Object.entries(reportData.cross_tables.by_status);
    const statusHeaders = ['Statut', 'Nombre'];
    const statusRows = statusData.map(([status, count]) => [status, count.toString()]);

    doc.autoTable({
      head: [statusHeaders],
      body: statusRows,
      startY: yPosition,
      styles: { fontSize: 10 },
      headStyles: { fillColor: [66, 139, 202] }
    });

    yPosition = doc.lastAutoTable.finalY + 15;

    // Cross-table by Pilote
    doc.setFontSize(14);
    doc.text('RÉPARTITION PAR PILOTE', 20, yPosition);
    yPosition += 10;

    const piloteData = Object.entries(reportData.cross_tables.by_pilote);
    const piloteHeaders = ['Pilote', 'Sourcing', 'Dealflow', 'Total'];
    const piloteRows = piloteData.map(([pilote, data]) => [
      pilote, 
      data.sourcing.toString(), 
      data.dealflow.toString(), 
      data.total.toString()
    ]);

    doc.autoTable({
      head: [piloteHeaders],
      body: piloteRows,
      startY: yPosition,
      styles: { fontSize: 10 },
      headStyles: { fillColor: [66, 139, 202] }
    });

    // Add new page if needed
    if (doc.lastAutoTable.finalY > 250) {
      doc.addPage();
      yPosition = 20;
    } else {
      yPosition = doc.lastAutoTable.finalY + 15;
    }

    // Cross-table by Domain
    doc.setFontSize(14);
    doc.text('RÉPARTITION PAR DOMAINE', 20, yPosition);
    yPosition += 10;

    const domainData = Object.entries(reportData.cross_tables.by_domain);
    const domainHeaders = ['Domaine', 'Sourcing', 'Dealflow', 'Total'];
    const domainRows = domainData.map(([domain, data]) => [
      domain, 
      data.sourcing.toString(), 
      data.dealflow.toString(), 
      data.total.toString()
    ]);

    doc.autoTable({
      head: [domainHeaders],
      body: domainRows,
      startY: yPosition,
      styles: { fontSize: 10 },
      headStyles: { fillColor: [66, 139, 202] }
    });

    doc.save(`SURM_Rapport_Synthetique_${currentDate.replace(/\//g, '-')}.pdf`);
  };

  const exportToCSV = () => {
    if (!reportData) return;

    const csvHeaders = [
      'Nom', 'Type', 'Statut', 'Domaine', 'Pilote', 'Typologie', 
      'Pays', 'Source', 'Date Entrée', 'Prochaine Action', 
      'Intérêt', 'Inactif', 'Actions/Commentaires'
    ];

    const csvData = [
      csvHeaders,
      ...reportData.detailed_data.map(row => [
        row.nom, row.type, row.statut, row.domaine, row.pilote,
        row.typologie, row.pays, row.source, row.date_entree,
        row.date_prochaine_action, row.interet, row.is_inactive,
        row.actions_commentaires
      ])
    ];

    const csvContent = csvData.map(row => 
      row.map(field => `"${field || ''}"`).join(',')
    ).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `SURM_Export_Detaille_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
  };

  if (!isVisible) return null;

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold">📊 Tableaux Synthétiques</h2>
            <p className="text-gray-600">Rapports croisés dynamiques pour comités d'innovation</p>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={exportToPDF}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 flex items-center space-x-2"
              disabled={!reportData}
            >
              <span>📄</span>
              <span>Export PDF</span>
            </button>
            <button
              onClick={exportToCSV}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 flex items-center space-x-2"
              disabled={!reportData}
            >
              <span>📊</span>
              <span>Export CSV</span>
            </button>
            <button
              onClick={loadReportData}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              🔄 Actualiser
            </button>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-2 text-gray-600">Génération des rapports...</p>
          </div>
        ) : reportData ? (
          <div className="space-y-8">
            {/* Summary */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{reportData.summary.total_sourcing}</div>
                <div className="text-sm text-gray-600">Total Sourcing</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{reportData.summary.total_dealflow}</div>
                <div className="text-sm text-gray-600">Total Dealflow</div>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">{reportData.summary.total_partners}</div>
                <div className="text-sm text-gray-600">Total Startups</div>
              </div>
              <div className="text-center p-4 bg-orange-50 rounded-lg">
                <div className="text-2xl font-bold text-orange-600">
                  {Object.keys(reportData.cross_tables.by_pilote).length}
                </div>
                <div className="text-sm text-gray-600">Pilotes Actifs</div>
              </div>
            </div>

            {/* Cross-Table by Pilote */}
            <div className="bg-gray-50 p-6 rounded-lg">
              <h3 className="text-lg font-semibold mb-4">📋 Répartition par Pilote</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full table-auto">
                  <thead>
                    <tr className="bg-blue-100">
                      <th className="px-4 py-2 text-left font-semibold">Pilote</th>
                      <th className="px-4 py-2 text-center font-semibold">Sourcing</th>
                      <th className="px-4 py-2 text-center font-semibold">Dealflow</th>
                      <th className="px-4 py-2 text-center font-semibold">Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(reportData.cross_tables.by_pilote).map(([pilote, data]) => (
                      <tr key={pilote} className="border-b hover:bg-gray-50">
                        <td className="px-4 py-2 font-medium">{pilote}</td>
                        <td className="px-4 py-2 text-center">{data.sourcing}</td>
                        <td className="px-4 py-2 text-center">{data.dealflow}</td>
                        <td className="px-4 py-2 text-center font-semibold">{data.total}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Cross-Table by Domain */}
            <div className="bg-gray-50 p-6 rounded-lg">
              <h3 className="text-lg font-semibold mb-4">🏢 Répartition par Domaine</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full table-auto">
                  <thead>
                    <tr className="bg-green-100">
                      <th className="px-4 py-2 text-left font-semibold">Domaine</th>
                      <th className="px-4 py-2 text-center font-semibold">Sourcing</th>
                      <th className="px-4 py-2 text-center font-semibold">Dealflow</th>
                      <th className="px-4 py-2 text-center font-semibold">Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(reportData.cross_tables.by_domain).map(([domain, data]) => (
                      <tr key={domain} className="border-b hover:bg-gray-50">
                        <td className="px-4 py-2 font-medium">{domain}</td>
                        <td className="px-4 py-2 text-center">{data.sourcing}</td>
                        <td className="px-4 py-2 text-center">{data.dealflow}</td>
                        <td className="px-4 py-2 text-center font-semibold">{data.total}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Status Distribution */}
            <div className="bg-gray-50 p-6 rounded-lg">
              <h3 className="text-lg font-semibold mb-4">📈 Répartition par Statut</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(reportData.cross_tables.by_status).map(([status, count]) => (
                  <div key={status} className="flex justify-between items-center p-3 bg-white rounded border">
                    <span className="text-sm font-medium">{status}</span>
                    <span className="text-lg font-bold text-blue-600">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            Erreur de chargement des données de rapport
          </div>
        )}
      </div>
    </div>
  );
};

// Phase 4 - Global Search Component (Streamlined)
const GlobalSearchBar = ({ onSearch, onQuickView }) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [showQuickMenu, setShowQuickMenu] = useState(false);
  const [showHamburgerMenu, setShowHamburgerMenu] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (searchQuery.trim().length < 2) return;
    
    setIsSearching(true);
    try {
      await onSearch(searchQuery.trim());
    } finally {
      setIsSearching(false);
    }
  };

  const quickViews = [
    { id: 'mes-startups', label: '👨‍💼 Mes Startups', color: 'purple' },
    { id: 'a-relancer', label: '⏰ À Relancer', color: 'red' },
    { id: 'avec-documents', label: '📄 Avec Docs', color: 'blue' },
    { id: 'en-experimentation', label: '🧪 En Expé', color: 'green' }
  ];

  const handleQuickViewSelect = (viewType) => {
    onQuickView(viewType);
    setShowQuickMenu(false);
  };

  return (
    <div className="flex items-center space-x-3">
      {/* Global Search */}
      <form onSubmit={handleSearch} className="flex items-center">
        <div className="relative">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Recherche globale..."
            className="w-72 pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            {isSearching ? (
              <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
            ) : (
              <svg className="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            )}
          </div>
        </div>
        <button
          type="submit"
          disabled={searchQuery.trim().length < 2 || isSearching}
          className="ml-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          🔍
        </button>
      </form>

      {/* Quick Views Dropdown - More Compact */}
      <div className="relative">
        <button
          onClick={() => setShowQuickMenu(!showQuickMenu)}
          className="px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 flex items-center space-x-1 text-sm"
        >
          <span>⚡</span>
          <span className="hidden md:inline">Vues</span>
          <svg className={`w-4 h-4 transition-transform ${showQuickMenu ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        
        {showQuickMenu && (
          <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border z-50">
            <div className="py-1">
              {quickViews.map(view => (
                <button
                  key={view.id}
                  onClick={() => handleQuickViewSelect(view.id)}
                  className="w-full px-3 py-2 text-left hover:bg-gray-50 flex items-center space-x-2 text-sm"
                >
                  <span>{view.label}</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Document Management Components
const DocumentUpload = ({ partnerId, partnerType, onDocumentUploaded }) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [documentType, setDocumentType] = useState('Autre');
  const [description, setDescription] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  
  const documentTypes = [
    { value: 'Convention', label: '📄 Convention' },
    { value: 'Présentation', label: '📊 Présentation' },
    { value: 'Compte-rendu', label: '📝 Compte-rendu' },
    { value: 'Contrat', label: '📋 Contrat' },
    { value: 'Document technique', label: '🔧 Document technique' },
    { value: 'Autre', label: '📎 Autre' }
  ];

  const convertToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        const base64 = reader.result.split(',')[1]; // Remove data:mime;base64, prefix
        resolve(base64);
      };
      reader.onerror = error => reject(error);
    });
  };

  const handleDragEnter = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  const handleFileUpload = async (file) => {
    if (!file) return;

    // Validate file type
    const allowedTypes = ['application/pdf', 'application/msword', 
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                          'application/vnd.ms-powerpoint',
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                          'text/plain', 'image/jpeg', 'image/png'];
    
    if (!allowedTypes.includes(file.type)) {
      alert('Type de fichier non supporté. Utilisez PDF, DOC, DOCX, PPT, PPTX, TXT, JPG ou PNG.');
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert('Fichier trop volumineux. Taille maximum: 10MB');
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);
    
    let progressInterval; // Declare outside try block

    try {
      // Simulate progress
      progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 100);

      // Convert to base64
      const base64Content = await convertToBase64(file);

      // Upload to backend using simple JSON (much more reliable)
      const uploadData = {
        partner_id: partnerId,
        partner_type: partnerType,
        filename: file.name,
        document_type: documentType,
        content: base64Content,
        description: description.trim() || '',
        uploaded_by: 'current_user'
      };
      
      console.log('🔼 ENVOI UPLOAD JSON - Données:', {
        partner_id: partnerId,
        filename: file.name,
        document_type: documentType,
        content_length: base64Content.length
      });
      
      const response = await axios.post(`${API_URL}/documents/upload`, uploadData, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      console.log('✅ UPLOAD JSON RÉUSSI - Status:', response.status);

      clearInterval(progressInterval);
      setUploadProgress(100);
      
      // Reset form
      setDescription('');
      setDocumentType('Autre');
      
      // Callback to parent component
      onDocumentUploaded && onDocumentUploaded(response.data);
      
      setTimeout(() => {
        setUploadProgress(0);
        setIsUploading(false);
      }, 1000);

    } catch (error) {
      console.error('❌ ERREUR UPLOAD - Document:', error);
      if (progressInterval) clearInterval(progressInterval);
      
      // Detailed error handling
      let errorMessage = '🔼 ERREUR UPLOAD: ';
      if (error.response) {
        const status = error.response.status;
        const responseText = error.response.data?.detail || error.response.data || 'Erreur inconnue';
        
        if (status === 400) {
          errorMessage += `Données invalides (400): ${responseText}`;
        } else if (status === 422) {
          errorMessage += `Validation échouée (422): ${responseText}`;
        } else if (status === 500) {
          errorMessage += `Erreur serveur (500): ${responseText}`;
        } else {
          errorMessage += `Erreur HTTP ${status}: ${responseText}`;
        }
      } else if (error.request) {
        errorMessage += 'Impossible de contacter le serveur. Vérifiez votre connexion.';
      } else {
        errorMessage += `Erreur: ${error.message}`;
      }
      
      alert(errorMessage);
      console.error('📊 DÉTAILS ERREUR UPLOAD:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        config: {
          url: error.config?.url,
          method: error.config?.method,
          headers: error.config?.headers
        }
      });
      
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  return (
    <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 bg-gray-50">
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Type de document
        </label>
        <select
          value={documentType}
          onChange={(e) => setDocumentType(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {documentTypes.map(type => (
            <option key={type.value} value={type.value}>
              {type.label}
            </option>
          ))}
        </select>
      </div>

      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Description (optionnel)
        </label>
        <input
          type="text"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Description du document..."
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer ${
          isDragOver 
            ? 'border-blue-400 bg-blue-50' 
            : 'border-gray-400 hover:border-gray-500'
        } ${isUploading ? 'opacity-50 pointer-events-none' : ''}`}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={() => document.getElementById(`file-upload-${partnerId}`).click()}
      >
        {isUploading ? (
          <div className="space-y-3">
            <div className="text-lg">📤 Upload en cours...</div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
            <div className="text-sm text-gray-600">{uploadProgress}%</div>
          </div>
        ) : (
          <div className="space-y-2">
            <div className="text-4xl mb-2">📎</div>
            <div className="text-lg font-medium text-gray-700">
              Glissez-déposez vos fichiers ici
            </div>
            <div className="text-sm text-gray-500">
              ou cliquez pour sélectionner
            </div>
            <div className="text-xs text-gray-400">
              PDF, DOC, DOCX, PPT, PPTX, TXT, JPG, PNG (max 10MB)
            </div>
          </div>
        )}
        
        <input
          id={`file-upload-${partnerId}`}
          type="file"
          className="hidden"
          accept=".pdf,.doc,.docx,.ppt,.pptx,.txt,.jpg,.jpeg,.png"
          onChange={handleFileSelect}
        />
      </div>
    </div>
  );
};

const DocumentList = ({ partnerId, documents, onDeleteDocument, onRefreshDocuments }) => {
  const handleDownload = async (documentId, filename) => {
    try {
      console.log('🔽 DEBUT TELECHARGEMENT - Document ID:', documentId, 'Filename:', filename);
      console.log('🔽 URL BACKEND utilisée:', API_URL);
      
      const downloadUrl = `${API_URL}/documents/download/${documentId}`;
      console.log('🔽 URL complète de téléchargement:', downloadUrl);
      
      const response = await axios.get(downloadUrl, {
        responseType: 'blob'
      });
      
      console.log('🔽 Réponse reçue - Status:', response.status, 'Taille:', response.data.size);
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      console.log('✅ TELECHARGEMENT REUSSI:', filename);
      
    } catch (error) {
      console.error('❌ ERREUR TELECHARGEMENT - Document ID:', documentId, 'Error:', error);
      console.error('❌ Details erreur:', error.response?.status, error.response?.data);
      alert(`🔽 ERREUR TÉLÉCHARGEMENT: Impossible de télécharger le document "${filename}". Vérifiez votre connexion.`);
    }
  };

  const handleDelete = async (documentId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer ce document ?')) {
      return;
    }

    try {
      await axios.delete(`${API_URL}/documents/${documentId}`);
      onDeleteDocument && onDeleteDocument(documentId);
      onRefreshDocuments && onRefreshDocuments();
    } catch (error) {
      console.error('Error deleting document:', error);
      alert('Erreur lors de la suppression du document.');
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getDocumentIcon = (fileType) => {
    if (fileType.includes('pdf')) return '📄';
    if (fileType.includes('word') || fileType.includes('document')) return '📝';
    if (fileType.includes('powerpoint') || fileType.includes('presentation')) return '📊';
    if (fileType.includes('image')) return '🖼️';
    return '📎';
  };

  if (!documents || documents.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <div className="text-4xl mb-2">📁</div>
        <div>Aucun document attaché</div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {documents.map((doc) => (
        <div key={doc.id} className="bg-white border rounded-lg p-4 shadow-sm">
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-3 flex-1">
              <div className="text-2xl">
                {getDocumentIcon(doc.file_type)}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2 mb-1">
                  <h4 className="font-medium text-gray-900 truncate">
                    {doc.original_filename}
                  </h4>
                  {doc.version > 1 && (
                    <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                      v{doc.version}
                    </span>
                  )}
                </div>
                
                <div className="flex items-center space-x-4 text-sm text-gray-500">
                  <span className="bg-gray-100 px-2 py-1 rounded text-xs">
                    {doc.document_type}
                  </span>
                  <span>{formatFileSize(doc.file_size)}</span>
                  <span>{new Date(doc.uploaded_at).toLocaleDateString('fr-FR')}</span>
                </div>
                
                {doc.description && (
                  <p className="text-sm text-gray-600 mt-2 italic">
                    {doc.description}
                  </p>
                )}
              </div>
            </div>
            
            <div className="flex items-center space-x-2 ml-4">
              <button
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  console.log('🔽 CLIC BOUTON TELECHARGEMENT - Document:', doc.id, doc.filename);
                  handleDownload(doc.id, doc.filename);
                }}
                className="text-blue-600 hover:text-blue-800 p-1 rounded hover:bg-blue-50"
                title="Télécharger"
              >
                📥
              </button>
              <button
                onClick={() => handleDelete(doc.id)}
                className="text-red-600 hover:text-red-800 p-1 rounded hover:bg-red-50"
                title="Supprimer"
              >
                🗑️
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

// Phase 4 - Quick Views Component
const QuickViewResults = ({ isVisible, viewData, onClose }) => {
  if (!isVisible || !viewData) return null;

  const renderPartnerCard = (partner, type) => {
    const name = type === 'sourcing' ? partner.nom_entreprise : partner.nom;
    const domain = type === 'sourcing' ? partner.domaine_activite : partner.domaine;
    
    return (
      <div key={partner.id} className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
        <div className="flex justify-between items-start mb-2">
          <div className="flex-1">
            <h4 className="font-semibold text-gray-800">{name}</h4>
            <p className="text-sm text-gray-600">{domain}</p>
          </div>
          <div className="flex items-center space-x-2">
            {partner.is_inactive && (
              <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" title="Inactif"></span>
            )}
            <span className={`text-xs px-2 py-1 rounded ${type === 'sourcing' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'}`}>
              {type === 'sourcing' ? '🔍 Sourcing' : '🚀 Dealflow'}
            </span>
          </div>
        </div>
        
        <div className="text-xs text-gray-600 space-y-1">
          <div className="flex items-center space-x-2">
            <span>👤 {partner.pilote}</span>
            <span>📊 {partner.statut}</span>
          </div>
          
          {partner.date_prochaine_action && (
            <div className="flex items-center space-x-1">
              <span>📅</span>
              <span className={`font-medium ${
                new Date(partner.date_prochaine_action) < new Date() ? 'text-red-600' : 'text-green-600'
              }`}>
                {new Date(partner.date_prochaine_action).toLocaleDateString('fr-FR')}
              </span>
            </div>
          )}
          
          {partner.followup_reasons && (
            <div className="mt-2 text-red-600">
              <strong>À relancer:</strong>
              <ul className="list-disc list-inside ml-2">
                {partner.followup_reasons.map((reason, idx) => (
                  <li key={idx}>{reason}</li>
                ))}
              </ul>
            </div>
          )}
          
          {partner.document_types && (
            <div className="mt-2 text-blue-600">
              <strong>Documents:</strong> {partner.document_types.join(', ')}
            </div>
          )}
          
          {partner.experimentation_stage && (
            <div className="mt-2 text-green-600">
              <strong>Expérimentation:</strong> {partner.experimentation_stage}
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-6xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold">{viewData.view_name}</h2>
            <p className="text-gray-600">{viewData.description}</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ✕
          </button>
        </div>

        {/* Summary */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">{viewData.summary.sourcing_count}</div>
            <div className="text-sm text-gray-600">Sourcing</div>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">{viewData.summary.dealflow_count}</div>
            <div className="text-sm text-gray-600">Dealflow</div>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">{viewData.summary.total}</div>
            <div className="text-sm text-gray-600">Total</div>
          </div>
        </div>

        {/* Results */}
        <div className="space-y-6">
          {viewData.sourcing.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-4">🔍 Sourcing ({viewData.sourcing.length})</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {viewData.sourcing.map(partner => renderPartnerCard(partner, 'sourcing'))}
              </div>
            </div>
          )}
          
          {viewData.dealflow.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-4">🚀 Dealflow ({viewData.dealflow.length})</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {viewData.dealflow.map(partner => renderPartnerCard(partner, 'dealflow'))}
              </div>
            </div>
          )}
        </div>

        {viewData.summary.total === 0 && (
          <div className="text-center py-8 text-gray-500">
            Aucun résultat trouvé pour cette vue
          </div>
        )}

        <div className="flex justify-end mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
          >
            Fermer
          </button>
        </div>
      </div>
    </div>
  );
};
const translateToFrench = async (text) => {
  if (!text || typeof text !== "string") return "";

  try {
    const response = await fetch(
      "https://api.mymemory.translated.net/get?q=" +
        encodeURIComponent(text) +
        "&langpair=en|fr"
    );

    const data = await response.json();

    if (data?.responseData?.translatedText) {
      return data.responseData.translatedText;
    }

    return text;
  } catch (error) {
    console.error("❌ Erreur traduction :", error);
    return text;
  }
};
const SourcingForm = ({ onSubmit, initialData = null, onCancel, customFields = [], onChangeTab }) => {
  // État simple avec tous les champs requis + évaluation stratégique complète
  const [formData, setFormData] = useState({
    nom_entreprise: initialData?.nom_entreprise || "",
    statut: initialData?.statut || "A traiter",
    pays_origine: initialData?.pays_origine || "",
    domaine_activite: initialData?.domaine_activite || "",
    typologie: initialData?.typologie || "",
    objet: initialData?.objet || "",
    cas_usage: initialData?.cas_usage || "",
    technologie: initialData?.technologie || "",
    source: initialData?.source || "",
    date_entree_sourcing: initialData?.date_entree_sourcing || "",
    pilote: initialData?.pilote || "",
    interet: initialData?.interet || true,
    date_presentation_metiers: initialData?.date_presentation_metiers || "",
    actions_commentaires: initialData?.actions_commentaires || "",
    date_prochaine_action: initialData?.date_prochaine_action || "",
    // Évaluation stratégique complète
    score_maturite: initialData?.score_maturite || "",
    priorite_strategique: initialData?.priorite_strategique || "",
    score_potentiel: initialData?.score_potentiel || "",
    tags_strategiques: Array.isArray(initialData?.tags_strategiques) 
      ? initialData.tags_strategiques.join(', ') 
      : (initialData?.tags_strategiques || "")
  });

  // Phase 5 - Duplicate Detection
  const { duplicates, isChecking, checkDuplicates, clearDuplicates } = useDuplicateDetection();
  const [showDuplicateAlert, setShowDuplicateAlert] = useState(false);
  const [forcingCreation, setForcingCreation] = useState(false);

  // Phase 6 - Company Enrichment
  const { enrichCompany, isEnriching, enrichmentError, clearError } = useCompanyEnrichment();

  // Gestion simple des changements + tags stratégiques
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    if (name === 'tags_strategiques') {
      // Preserve the raw input for tags during typing (don't filter until submission)
      setFormData(prev => ({
        ...prev,
        [name]: value  // Keep as string during typing
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: type === 'checkbox' ? checked : value
      }));

      // Phase 5 - Check for duplicates when nom_entreprise changes
      if (name === 'nom_entreprise' && !initialData) { // Only check for new partners, not edits
        if (value.length >= 3) {
          checkDuplicates(value);
          setShowDuplicateAlert(true);
          setForcingCreation(false);
        } else {
          clearDuplicates();
          setShowDuplicateAlert(false);
          setForcingCreation(false);
        }
      }
    }
  };

  // Soumission simple et robuste
  const handleSubmit = (e) => {
    console.log("🚀 DÉBUT HANDLESUBMIT - Event reçu:", e);
    e.preventDefault();
    
    console.log("🔍 NOUVEAU FORMULAIRE SOURCING - Démarrage...");
    console.log("📋 Données du formulaire:", formData);
    console.log("📋 Type de données formData:", typeof formData);
    console.log("📋 Clés du formulaire:", Object.keys(formData));
    
    // Vérification des champs requis
    const requiredFields = {
      nom_entreprise: "Nom entreprise",
      statut: "Statut", 
      source: "Source",
      date_entree_sourcing: "Date d'entrée sourcing",
      };

    const missingFields = [];
    Object.entries(requiredFields).forEach(([field, label]) => {
      const value = formData[field];
      console.log(`🔍 VALIDATION - ${label}: "${value}"`);
      if (!value || (typeof value === 'string' && value.trim() === "")) {
        missingFields.push(label);
        console.log(`❌ CHAMP MANQUANT: ${label}`);
      }
    });

    console.log(`📊 VALIDATION RÉSULTATS: ${missingFields.length} champs manquants`);

    if (missingFields.length > 0) {
      alert(`❌ Veuillez remplir les champs obligatoires :\n• ${missingFields.join('\n• ')}\n\n📋 Debug: Vérifiez que tous les champs marqués d'un * sont remplis.`);
      console.log("❌ FORM SUBMISSION STOPPED - Missing required fields:", missingFields);
      return;
    }

    // Phase 5 - Check for duplicates before submission (only for new partners)
    if (!initialData && duplicates.length > 0 && !forcingCreation) {
      alert("⚠️ Des partenaires similaires existent déjà. Veuillez vérifier les suggestions ou forcer la création.");
      return;
    }

    console.log("✅ Validation réussie, envoi des données...");
    
    // Préparation des données pour l'API
    const apiData = { ...formData };
    
    console.log("🔄 CONVERSION TAGS - Avant:", apiData.tags_strategiques, typeof apiData.tags_strategiques);
    
    // Conversion des tags stratégiques (string -> array)
    if (typeof apiData.tags_strategiques === 'string') {
      apiData.tags_strategiques = apiData.tags_strategiques
        .split(',')
        .map(tag => tag.trim())
        .filter(tag => tag.length > 0);
    }
    
    console.log("🔄 CONVERSION TAGS - Après:", apiData.tags_strategiques);
    
    // Conversion des dates vides en null
    Object.keys(apiData).forEach(key => {
      if (key.includes('date') && apiData[key] === '') {
        apiData[key] = null;
      }
    });
    
    // Fix evaluation fields - convert empty/placeholder values to null
    if (apiData.score_maturite === '' || apiData.score_maturite === 'Non évalué' || !apiData.score_maturite) {
      apiData.score_maturite = null;
    }
    if (apiData.priorite_strategique === '' || apiData.priorite_strategique === 'Non définie' || !apiData.priorite_strategique) {
      apiData.priorite_strategique = null;
    }
    if (apiData.score_potentiel === '' || apiData.score_potentiel === 'Non évalué' || !apiData.score_potentiel) {
      apiData.score_potentiel = null;
    }
    
    console.log("🔄 NETTOYAGE CHAMPS ÉVALUATION - Après:", {
      score_maturite: apiData.score_maturite,
      priorite_strategique: apiData.priorite_strategique,
      score_potentiel: apiData.score_potentiel
    });

    console.log("📤 Données pour l'API (finales):", apiData);
    console.log("📤 Fonction onSubmit:", typeof onSubmit);
    
    try {
      console.log("🚀 APPEL onSubmit...");
      onSubmit(apiData);
      console.log("✅ onSubmit appelé avec succès");
    } catch (error) {
      console.error("❌ ERREUR lors de onSubmit:", error);
      alert("❌ Erreur lors de la soumission: " + error.message);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-6 text-center">
          {initialData ? "Modifier" : "Nouveau"} Partenaire Sourcing
        </h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Champs obligatoires - Structure simple linéaire */}
          
          <div>
            <label className="block text-sm font-medium mb-2">
              Nom entreprise <span className="text-red-500">*</span>
            </label>
            <div className="flex space-x-2">
              <input
                type="text"
                name="nom_entreprise"
                value={formData.nom_entreprise}
                onChange={handleChange}
                className="flex-1 border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Nom de l'entreprise"
              />
                <button
                type="button"
                onClick={async () => {
                  if (!formData.nom_entreprise || formData.nom_entreprise.length < 3) {
                    alert("Veuillez saisir au moins 3 caractères pour enrichir les données");
                    return;
                  }
                  clearError();
                  const enrichedData = await enrichCompany(formData.nom_entreprise);
                  const descriptionFR = enrichedData?.description
                    ? await translateToFrench(enrichedData.description)
                    : "";

                  console.log('🔍 ENRICHISSEMENT - Données reçues:', enrichedData);
                  console.log('🇫🇷 DESCRIPTION TRADUITE :', descriptionFR);

                  if (enrichedData) {
                    // Smart mapping function for enriched data to dropdown values
                    const mapIndustryToDomain = (industry) => {
                      if (!industry) return null;
                      const industryLower = industry.toLowerCase();

                      if (industryLower.includes("fintech") || industryLower.includes("financial technology")) return "FinTech";
                      if (industryLower.includes("insurtech") || industryLower.includes("insurance")) return "InsurTech";
                      if (industryLower.includes("legaltech") || industryLower.includes("legal")) return "LegalTech";
                      if (industryLower.includes("edtech") || industryLower.includes("education")) return "EdTech";
                      if (industryLower.includes("healthtech") || industryLower.includes("health") || industryLower.includes("medical")) return "DigitalHealth";
                      if (industryLower.includes("proptech") || industryLower.includes("real estate")) return "PropTech";
                      if (industryLower.includes("martech") || industryLower.includes("marketing")) return "MarTech";
                      if (industryLower.includes("retailtech") || industryLower.includes("retail")) return "RetailTech";
                      if (industryLower.includes("mobility") || industryLower.includes("transport")) return "Mobility";
                      if (industryLower.includes("cyber") || industryLower.includes("security")) return "CyberSecurity";
                      if (industryLower.includes("data") || industryLower.includes("analytics")) return "Data";
                      if (industryLower.includes("clean") || industryLower.includes("green") || industryLower.includes("environment")) return "CleanTech";
                      if (industryLower.includes("climate")) return "ClimateTech";
                      if (industryLower.includes("tech") || industryLower.includes("technology") || industryLower.includes("software")) return "Tech";
                      if (industryLower.includes("consult")) return "Conseil";

                      return "Autre";
                    };

                    const mapCountryToPays = (country) => {
                      if (!country) return null;
                      const countryLower = country.toLowerCase();

                      if (countryLower.includes("france") || countryLower.includes("french")) return "France";
                      if (countryLower.includes("germany") || countryLower.includes("allemagne")) return "Allemagne";
                      if (countryLower.includes("united states") || countryLower.includes("usa") || countryLower.includes("america")) return "États-Unis";
                      if (countryLower.includes("united kingdom") || countryLower.includes("uk") || countryLower.includes("britain")) return "Royaume-Uni";
                      if (countryLower.includes("spain") || countryLower.includes("espagne")) return "Espagne";
                      if (countryLower.includes("italy") || countryLower.includes("italie")) return "Italie";
                      if (countryLower.includes("switzerland") || countryLower.includes("suisse")) return "Suisse";
                      if (countryLower.includes("belgium") || countryLower.includes("belgique")) return "Belgique";

                      return "Autre";
                    };

                    const updatedData = {
                      ...formData,
                      domaine_activite:
                        (!formData.domaine_activite || formData.domaine_activite === "") && enrichedData.industry
                          ? mapIndustryToDomain(enrichedData.industry)
                          : formData.domaine_activite,
                      pays_origine:
                        (!formData.pays_origine || formData.pays_origine === "") && enrichedData.country
                          ? mapCountryToPays(enrichedData.country)
                          : formData.pays_origine,
                      typologie:
                        (!formData.typologie || formData.typologie === "") && enrichedData.company_type
                          ? (
                              enrichedData.company_type === "startup" ||
                              enrichedData.company_type.toLowerCase().includes("startup")
                            )
                            ? "Startup"
                            : (
                                enrichedData.company_type === "private" ||
                                enrichedData.company_type.toLowerCase().includes("private")
                              )
                              ? "PME"
                              : enrichedData.employees_count && enrichedData.employees_count > 250
                                ? "Scale-up"
                                : "Startup"
                          : formData.typologie,
                      objet:
                        (!formData.objet || formData.objet === "") && descriptionFR
                          ? descriptionFR.substring(0, 200) + (descriptionFR.length > 200 ? "..." : "")
                          : formData.objet,
                      technologie:
                        (!formData.technologie || formData.technologie === "") &&
                        enrichedData.industry &&
                        enrichedData.industry.toLowerCase().includes("tech")
                          ? enrichedData.industry
                          : formData.technologie
                    };

                    console.log("📋 APRÈS ENRICHISSEMENT:", updatedData);

                    setFormData(updatedData);

                    const filledFields = [];
                    const mappingDetails = [];

                    if (enrichedData.industry && (!formData.domaine_activite || formData.domaine_activite === "")) {
                      filledFields.push("Domaine d'activité");
                      mappingDetails.push(`🎯 ${enrichedData.industry} → ${updatedData.domaine_activite}`);
                    }

                    if (enrichedData.country && (!formData.pays_origine || formData.pays_origine === "")) {
                      filledFields.push("Pays d'origine");
                      mappingDetails.push(`🌍 ${enrichedData.country} → ${updatedData.pays_origine}`);
                    }

                    if (enrichedData.description && (!formData.objet || formData.objet === "")) {
                      filledFields.push("Description");
                      mappingDetails.push(`📝 Description ajoutée (${enrichedData.description.length} caractères)`);
                    }

                    if (enrichedData.company_type && (!formData.typologie || formData.typologie === "")) {
                      filledFields.push("Typologie");
                      mappingDetails.push(`🏢 ${enrichedData.company_type} → ${updatedData.typologie}`);
                    }

                    if (filledFields.length > 0) {
                      alert(
                        `✅ Données enrichies avec succès !\n\n🏢 Champs remplis: ${filledFields.join(", ")}\n\n🔄 Mappings effectués:\n${mappingDetails.join("\n")}\n\n📊 Données source:\n🏢 Secteur: ${enrichedData.industry || "N/A"}\n🌍 Pays: ${enrichedData.country || "N/A"}\n👥 Employés: ${enrichedData.employees_count || "N/A"}`
                      );
                    } else {
                      alert(
                        `ℹ️ Enrichissement réussi mais aucun nouveau champ à remplir.\n\n📊 Données trouvées:\n🏢 Secteur: ${enrichedData.industry || "N/A"}\n🌍 Pays: ${enrichedData.country || "N/A"}\n👥 Employés: ${enrichedData.employees_count || "N/A"}\n\n💡 Conseil: Videz les champs que vous souhaitez enrichir automatiquement.`
                      );
                    }
                  } else {
                    alert("❌ Aucune donnée trouvée pour enrichir cette entreprise. Essayez avec le nom de domaine (ex: google.com) ou vérifiez l'orthographe.");
                  }
                }}
                disabled={isEnriching || !formData.nom_entreprise || formData.nom_entreprise.length < 3}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  isEnriching || !formData.nom_entreprise || formData.nom_entreprise.length < 3
                    ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                    : "bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                }`}
                title="Enrichir automatiquement les données de l'entreprise"
              >
                {isEnriching ? (
                  <span className="flex items-center space-x-1">
                    <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>...</span>
                  </span>
                ) : (
                  "🔍 Enrichir"
                )}
              </button>
            </div>
            
            {/* Phase 6 - Enrichment Error Display */}
            {enrichmentError && (
              <div className="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded text-sm text-yellow-800">
                ⚠️ {enrichmentError}
              </div>
            )}
            
            {/* Phase 5 - Duplicate Detection Alert */}
            {showDuplicateAlert && duplicates.length > 0 && (
              <DuplicateAlert
                duplicates={duplicates}
                onViewPartner={(duplicate) => {
                  console.log('🔍 VOIR FICHE - Partenaire:', duplicate);
                  
                  // Close duplicate alert first
                  setShowDuplicateAlert(false);
                  clearDuplicates();
                  
                  // Simple approach: just show info about the duplicate and let user navigate manually
                  alert(`📋 Partenaire similaire trouvé :\n\n🏢 Nom: ${duplicate.name}\n📊 Type: ${duplicate.type === 'sourcing' ? 'Sourcing' : 'Dealflow'}\n🎯 Similarité: ${duplicate.similarity * 100}%\n🏭 Domaine: ${duplicate.domain || 'N/A'}\n📍 Statut: ${duplicate.status || 'N/A'}\n👤 Pilote: ${duplicate.pilot || 'N/A'}\n\n💡 Pour consulter la fiche complète, allez dans l'onglet ${duplicate.type === 'sourcing' ? 'Sourcing' : 'Dealflow'} et recherchez "${duplicate.name}".`);
                  
                  // Optionally switch to the right tab
                  if (onChangeTab) {
                    if (duplicate.type === 'dealflow') {
                      onChangeTab('dealflow');
                    } else if (duplicate.type === 'sourcing') {
                      onChangeTab('sourcing');
                    }
                  }
                }}
                onCreateAnyway={() => {
                  setForcingCreation(true);
                  setShowDuplicateAlert(false);
                }}
                onCancel={() => {
                  setFormData(prev => ({ ...prev, nom_entreprise: '' }));
                  setShowDuplicateAlert(false);
                  clearDuplicates();
                }}
              />
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Statut <span className="text-red-500">*</span>
              </label>
              <select
                name="statut"
                value={formData.statut}
                onChange={handleChange}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="A traiter">A traiter</option>
                <option value="Clos">Clos</option>
                <option value="Dealflow">Dealflow</option>
                <option value="Klaxoon">Klaxoon</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Pays d'origine 
              </label>
              <input
                type="text"
                name="pays_origine"
                value={formData.pays_origine}
                onChange={handleChange}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="France"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Domaine d'activité 
            </label>
            <select
              name="domaine_activite"
              value={formData.domaine_activite}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Sélectionnez un domaine...</option>
              {DOMAINES_ACTIVITE.map(domaine => (
                <option key={domaine} value={domaine}>{domaine}</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Typologie 
              </label>
              <input
                type="text"
                name="typologie"
                value={formData.typologie}
                onChange={handleChange}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Startup, PME, Scale-up..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Technologie 
              </label>
              <input
                type="text"
                name="technologie"
                value={formData.technologie}
                onChange={handleChange}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="IA, Blockchain, IoT..."
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Objet 
            </label>
            <input
              type="text"
              name="objet"
              value={formData.objet}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Description de la solution..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Cas d'usage 
            </label>
            <input
              type="text"
              name="cas_usage"
              value={formData.cas_usage}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Application concrète..."
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Source <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                name="source"
                value={formData.source}
                onChange={handleChange}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="VivaTech, LinkedIn, Partenariat..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Date d'entrée sourcing <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                name="date_entree_sourcing"
                value={formData.date_entree_sourcing}
                onChange={handleChange}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Pilote 
            </label>
            <input
              type="text"
              name="pilote"
              value={formData.pilote}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Nom du pilote responsable"
            />
          </div>

          {/* Évaluation stratégique complète */}
          <div className="border-t pt-6">
            <div className="bg-blue-50 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-blue-800 mb-4">🎯 Évaluation Stratégique</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Score de Maturité */}
                <div>
                  <label className="block text-sm font-medium mb-2">Score de Maturité</label>
                  <select
                    name="score_maturite"
                    value={formData.score_maturite}
                    onChange={handleChange}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Non évalué</option>
                    {SCORE_MATURITE.map(score => (
                      <option key={score.value} value={score.value}>
                        {score.label} {score.stars}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Priorité Stratégique */}
                <div>
                  <label className="block text-sm font-medium mb-2">Priorité Stratégique</label>
                  <select
                    name="priorite_strategique"
                    value={formData.priorite_strategique}
                    onChange={handleChange}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Non définie</option>
                    {Object.entries(PRIORITE_STRATEGIQUE).map(([key, priorite]) => (
                      <option key={key} value={key}>
                        {priorite.icon} {priorite.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Score Potentiel */}
                <div>
                  <label className="block text-sm font-medium mb-2">Score Potentiel (1-10)</label>
                  <select
                    name="score_potentiel"
                    value={formData.score_potentiel}
                    onChange={handleChange}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Non évalué</option>
                    {[...Array(10)].map((_, i) => (
                      <option key={i+1} value={i+1}>
                        {i+1}/10 {"⭐".repeat(Math.ceil((i+1)/2))}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              
              {/* Tags Stratégiques */}
              <div className="mt-4">
                <label className="block text-sm font-medium mb-2">Tags Stratégiques</label>
                <input
                  type="text"
                  name="tags_strategiques"
                  value={formData.tags_strategiques || ''}
                  onChange={handleChange}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Ex: Innovation, Partenariat, B2B, Scaling..."
                />
                <p className="text-xs text-gray-500 mt-1">Séparez les tags par des virgules</p>
              </div>
            </div>
          </div>

          {/* Champs optionnels */}
          <div className="border-t pt-4">
            <h3 className="text-lg font-medium mb-3">Informations complémentaires</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Date présentation métiers</label>
                <input
                  type="date"
                  name="date_presentation_metiers"
                  value={formData.date_presentation_metiers}
                  onChange={handleChange}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Date prochaine action</label>
                <input
                  type="date"
                  name="date_prochaine_action"
                  value={formData.date_prochaine_action}
                  onChange={handleChange}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div className="mt-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  name="interet"
                  checked={formData.interet}
                  onChange={handleChange}
                  className="mr-2 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="text-sm font-medium">Intérêt confirmé</span>
              </label>
            </div>

            <div className="mt-4">
              <label className="block text-sm font-medium mb-2">Actions / Commentaires</label>
              <textarea
                name="actions_commentaires"
                value={formData.actions_commentaires}
                onChange={handleChange}
                rows={3}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Notes et commentaires..."
              />
            </div>
          </div>

          {/* Boutons d'action */}
          <div className="flex justify-end space-x-3 pt-6 border-t">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              Annuler
            </button>
            <button
              type="submit"
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {initialData ? "Modifier" : "Créer"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const DealflowForm = ({ onSubmit, initialData = null, onCancel, customFields = [], onChangeTab }) => {
  const [formData, setFormData] = useState({
    nom: initialData?.nom || "",
    statut: initialData?.statut || "En cours avec l'équipe inno",
    domaine: initialData?.domaine || "",
    typologie: initialData?.typologie || "",
    objet: initialData?.objet || "",
    source: initialData?.source || "",
    pilote: initialData?.pilote || "",
    metiers_concernes: initialData?.metiers_concernes || "",
    date_reception_fichier: initialData?.date_reception_fichier || "",
    date_pre_qualification: initialData?.date_pre_qualification || "",
    date_presentation_meetup_referents: initialData?.date_presentation_meetup_referents || "",
    date_presentation_metiers: initialData?.date_presentation_metiers || "",
    date_go_metier_etude: initialData?.date_go_metier_etude || "",
    date_go_experimentation: initialData?.date_go_experimentation || "",
    date_go_generalisation: initialData?.date_go_generalisation || "",
    date_cloture: initialData?.date_cloture || "",
    actions_commentaires: initialData?.actions_commentaires || "",
    points_etapes_intermediaires: initialData?.points_etapes_intermediaires || "",
    // Phase 1 - Suivi & Relance
    date_prochaine_action: initialData?.date_prochaine_action || "",
    // Scoring fields
    score_maturite: initialData?.score_maturite || "",
    priorite_strategique: initialData?.priorite_strategique || "",
    score_potentiel: initialData?.score_potentiel || "",
    tags_strategiques: Array.isArray(initialData?.tags_strategiques) 
      ? initialData.tags_strategiques.join(', ') 
      : (initialData?.tags_strategiques || ""),
    custom_fields: initialData?.custom_fields || {},
    ...customFields.reduce((acc, field) => {
      acc[field.name] = initialData?.[field.name] || field.defaultValue || "";
      return acc;
    }, {})
  });

  // Phase 5 - Duplicate Detection  
  const { duplicates, isChecking, checkDuplicates, clearDuplicates } = useDuplicateDetection();
  const [showDuplicateAlert, setShowDuplicateAlert] = useState(false);
  const [forcingCreation, setForcingCreation] = useState(false);

  // Phase 6 - Company Enrichment
  const { enrichCompany, isEnriching, enrichmentError, clearError } = useCompanyEnrichment();

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Ensure all required fields are filled
    if (!formData.nom || !formData.domaine || !formData.typologie || !formData.objet || 
        !formData.source || !formData.pilote || !formData.metiers_concernes || 
        !formData.date_reception_fichier) {
      alert("Veuillez remplir tous les champs requis marqués d'un *");
      return;
    }

    // Phase 5 - Check for duplicates before submission (only for new partners)
    if (!initialData && duplicates.length > 0 && !forcingCreation) {
      alert("⚠️ Des partenaires similaires existent déjà. Veuillez vérifier les suggestions ou forcer la création.");
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

      // Phase 5 - Check for duplicates when nom changes
      if (name === 'nom' && !initialData) { // Only check for new partners, not edits
        if (value.length >= 3) {
          checkDuplicates(value);
          setShowDuplicateAlert(true);
          setForcingCreation(false);
        } else {
          clearDuplicates();
          setShowDuplicateAlert(false);
          setForcingCreation(false);
        }
      }
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
              <div className="flex space-x-2">
                <input
                  type="text"
                  name="nom"
                  value={formData.nom}
                  onChange={handleChange}
                  required
                  className="flex-1 border rounded-md px-3 py-2"
                />
                <button
                  type="button"
                  onClick={async () => {
                    if (!formData.nom || formData.nom.length < 3) {
                      alert('Veuillez saisir au moins 3 caractères pour enrichir les données');
                      return;
                    }
                    
                    clearError();
                    const enrichedData = await enrichCompany(formData.nom);
                    
                    console.log('🔍 ENRICHISSEMENT DEALFLOW - Données reçues:', enrichedData);
                    
                    if (enrichedData) {
                      // Debug: Log current form data before update
                      console.log('📋 DEALFLOW AVANT ENRICHISSEMENT:', formData);
                      
                      // Auto-fill form fields with enriched data
                      const updatedData = {
                        ...formData,
                        domaine: enrichedData.industry && (!formData.domaine || formData.domaine === '') 
                          ? enrichedData.industry : formData.domaine,
                        typologie: enrichedData.company_type && (!formData.typologie || formData.typologie === '') ? 
                          (enrichedData.company_type === 'startup' ? 'Startup' : 
                           enrichedData.company_type === 'private' ? 'PME' : 
                           enrichedData.employees_count && enrichedData.employees_count > 250 ? 'Scale-up' : 
                           formData.typologie) : formData.typologie,
                        objet: enrichedData.description && (!formData.objet || formData.objet === '') 
                          ? enrichedData.description : formData.objet
                      };
                      
                      console.log('📋 DEALFLOW APRÈS ENRICHISSEMENT:', updatedData);
                      
                      setFormData(updatedData);
                      
                      // Count filled fields
                      const filledFields = [];
                      if (enrichedData.industry && (!formData.domaine || formData.domaine === '')) filledFields.push('Domaine');
                      if (enrichedData.description && (!formData.objet || formData.objet === '')) filledFields.push('Description');
                      
                      if (filledFields.length > 0) {
                        alert(`✅ Données enrichies avec succès !\n\n🏢 Champs remplis: ${filledFields.join(', ')}\n\n📊 Source: ${enrichedData.name || 'N/A'}\n🏢 Secteur: ${enrichedData.industry || 'N/A'}\n🌍 Pays: ${enrichedData.country || 'N/A'}\n👥 Employés: ${enrichedData.employees_count || 'N/A'}`);
                      } else {
                        alert(`ℹ️ Enrichissement réussi mais aucun nouveau champ à remplir.\n\n📊 Données trouvées:\n🏢 Secteur: ${enrichedData.industry || 'N/A'}\n🌍 Pays: ${enrichedData.country || 'N/A'}\n👥 Employés: ${enrichedData.employees_count || 'N/A'}`);
                      }
                    } else {
                      alert('❌ Aucune donnée trouvée pour enrichir cette entreprise. Essayez avec le nom de domaine ou vérifiez l\'orthographe.');
                    }
                  }}
                  disabled={isEnriching || !formData.nom || formData.nom.length < 3}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    isEnriching || !formData.nom || formData.nom.length < 3
                      ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                      : 'bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500'
                  }`}
                  title="Enrichir automatiquement les données de l'entreprise"
                >
                  {isEnriching ? (
                    <span className="flex items-center space-x-1">
                      <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <span>...</span>
                    </span>
                  ) : (
                    '🔍 Enrichir'
                  )}
                </button>
              </div>
              
              {/* Phase 6 - Enrichment Error Display */}
              {enrichmentError && (
                <div className="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded text-sm text-yellow-800">
                  ⚠️ {enrichmentError}
                </div>
              )}
              
              {/* Phase 5 - Duplicate Detection Alert */}
              {showDuplicateAlert && duplicates.length > 0 && (
                <DuplicateAlert
                  duplicates={duplicates}
                  onViewPartner={(duplicate) => {
                    console.log('🔍 VOIR FICHE DEALFLOW - Partenaire:', duplicate);
                    
                    // Close duplicate alert first
                    setShowDuplicateAlert(false);
                    clearDuplicates();
                    
                    // Simple approach: show info and guide user to navigate manually
                    alert(`📋 Partenaire similaire trouvé :\n\n🏢 Nom: ${duplicate.name}\n📊 Type: ${duplicate.type === 'sourcing' ? 'Sourcing' : 'Dealflow'}\n🎯 Similarité: ${duplicate.similarity * 100}%\n🏭 Domaine: ${duplicate.domain || 'N/A'}\n📍 Statut: ${duplicate.status || 'N/A'}\n👤 Pilote: ${duplicate.pilot || 'N/A'}\n\n💡 Pour consulter la fiche complète, allez dans l'onglet ${duplicate.type === 'sourcing' ? 'Sourcing' : 'Dealflow'} et recherchez "${duplicate.name}".`);
                    
                    // Switch to the appropriate tab
                    if (onChangeTab) {
                      if (duplicate.type === 'sourcing') {
                        onChangeTab('sourcing');
                      } else if (duplicate.type === 'dealflow') {
                        onChangeTab('dealflow');
                      }
                    }
                  }}
                  onCreateAnyway={() => {
                    setForcingCreation(true);
                    setShowDuplicateAlert(false);
                    clearDuplicates();
                  }}
                  onCancel={() => {
                    setShowDuplicateAlert(false);
                    clearDuplicates();
                    setFormData(prev => ({ ...prev, nom: '' }));
                  }}
                />
              )}
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
              <select
                name="domaine"
                value={formData.domaine}
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
            
            {/* Phase 1 - Date prochaine action */}
            <div>
              <label className="block text-sm font-medium mb-1">📅 Date prochaine action</label>
              <input
                type="date"
                name="date_prochaine_action"
                value={formData.date_prochaine_action}
                onChange={handleChange}
                className="w-full border rounded-md px-3 py-2"
                title="Planifier la prochaine action à effectuer"
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
      priorite_strategique: { visible: true, label: "Priorité" },
      score_maturite: { visible: true, label: "Maturité" },
      score_potentiel: { visible: false, label: "Potentiel" },
      tags_strategiques: { visible: false, label: "Tags" },
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
      priorite_strategique: { visible: true, label: "Priorité" },
      score_maturite: { visible: false, label: "Maturité" },
      score_potentiel: { visible: false, label: "Potentiel" },
      tags_strategiques: { visible: false, label: "Tags" },
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
      const sourcingConfig = await axios.get(`${API_URL}/config/form/sourcing`);
      const dealflowConfig = await axios.get(`${API_URL}/config/form/dealflow`);
      setFormConfig({
        sourcing: sourcingConfig.data,
        dealflow: dealflowConfig.data
      });

      // Load column configurations
      const columnConfigResponse = await axios.get(`${API_URL}/config/columns`);
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
      await axios.post(`${API_URL}/config/form`, {
        form_type: "sourcing",
        fields: formConfig.sourcing.fields || []
      });
      
      await axios.post(`${API_URL}/config/form`, {
        form_type: "dealflow",
        fields: formConfig.dealflow.fields || []
      });

      // Save column configurations
      await axios.post(`${API_URL}/config/columns`, columnConfig);
      
      // Save permissions with correct structure and valid enum values
      const permissionData = {
        user_id: "current_user",
        role: "contributeur", // Use valid backend enum value
        permissions: permissions.permissions || {} // Ensure it's a Dict[str, bool]
      };
      
      await axios.post(`${API_URL}/config/permissions`, permissionData);
      
      // Save enrichment settings
      await axios.post(`${API_URL}/config/enrichment`, enrichmentSettings);
      
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

const AdvancedFilters = ({ isOpen, onClose, onApplyFilters, filterType }) => {
  const [filters, setFilters] = useState({
    domaine: "",
    statut: "",
    typologie: "",
    pays: "",
    source: "",
    pilote: "",
    date_debut: "",
    date_fin: "",
    interet: ""
  });

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleApply = () => {
    onApplyFilters(filters);
    onClose();
  };

  const handleReset = () => {
    setFilters({
      domaine: "",
      statut: "",
      typologie: "",
      pays: "",
      source: "",
      pilote: "",
      date_debut: "",
      date_fin: "",
      interet: ""
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Filtres Avancés - {filterType === 'sourcing' ? 'Sourcing' : 'Dealflow'}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-2xl">✕</button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
          {/* Domaine Filter */}
          <div>
            <label className="block text-sm font-medium mb-2">Domaine</label>
            <select
              value={filters.domaine}
              onChange={(e) => handleFilterChange('domaine', e.target.value)}
              className="w-full border rounded-md px-3 py-2"
            >
              <option value="">Tous les domaines</option>
              {DOMAINES_ACTIVITE.map(domaine => (
                <option key={domaine} value={domaine}>{domaine}</option>
              ))}
            </select>
          </div>

          {/* Status Filter */}
          <div>
            <label className="block text-sm font-medium mb-2">Statut</label>
            <select
              value={filters.statut}
              onChange={(e) => handleFilterChange('statut', e.target.value)}
              className="w-full border rounded-md px-3 py-2"
            >
              <option value="">Tous les statuts</option>
              {(filterType === 'sourcing' ? FILTER_OPTIONS.statuts_sourcing : FILTER_OPTIONS.statuts_dealflow).map(statut => (
                <option key={statut} value={statut}>{statut}</option>
              ))}
            </select>
          </div>

          {/* Typologie Filter */}
          <div>
            <label className="block text-sm font-medium mb-2">Typologie</label>
            <select
              value={filters.typologie}
              onChange={(e) => handleFilterChange('typologie', e.target.value)}
              className="w-full border rounded-md px-3 py-2"
            >
              <option value="">Toutes les typologies</option>
              {FILTER_OPTIONS.typologies.map(typo => (
                <option key={typo} value={typo}>{typo}</option>
              ))}
            </select>
          </div>

          {/* Pays Filter */}
          <div>
            <label className="block text-sm font-medium mb-2">Pays</label>
            <select
              value={filters.pays}
              onChange={(e) => handleFilterChange('pays', e.target.value)}
              className="w-full border rounded-md px-3 py-2"
            >
              <option value="">Tous les pays</option>
              {FILTER_OPTIONS.pays.map(pays => (
                <option key={pays} value={pays}>{pays}</option>
              ))}
            </select>
          </div>

          {/* Source Filter */}
          <div>
            <label className="block text-sm font-medium mb-2">Source</label>
            <select
              value={filters.source}
              onChange={(e) => handleFilterChange('source', e.target.value)}
              className="w-full border rounded-md px-3 py-2"
            >
              <option value="">Toutes les sources</option>
              {FILTER_OPTIONS.sources.map(source => (
                <option key={source} value={source}>{source}</option>
              ))}
            </select>
          </div>

          {/* Pilote Filter */}
          <div>
            <label className="block text-sm font-medium mb-2">Pilote</label>
            <input
              type="text"
              value={filters.pilote}
              onChange={(e) => handleFilterChange('pilote', e.target.value)}
              placeholder="Nom du pilote"
              className="w-full border rounded-md px-3 py-2"
            />
          </div>

          {/* Date Range */}
          <div>
            <label className="block text-sm font-medium mb-2">Date début</label>
            <input
              type="date"
              value={filters.date_debut}
              onChange={(e) => handleFilterChange('date_debut', e.target.value)}
              className="w-full border rounded-md px-3 py-2"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Date fin</label>
            <input
              type="date"
              value={filters.date_fin}
              onChange={(e) => handleFilterChange('date_fin', e.target.value)}
              className="w-full border rounded-md px-3 py-2"
            />
          </div>

          {/* Interet Filter (Sourcing only) */}
          {filterType === 'sourcing' && (
            <div>
              <label className="block text-sm font-medium mb-2">Intérêt</label>
              <select
                value={filters.interet}
                onChange={(e) => handleFilterChange('interet', e.target.value)}
                className="w-full border rounded-md px-3 py-2"
              >
                <option value="">Tous</option>
                <option value="true">Oui</option>
                <option value="false">Non</option>
              </select>
            </div>
          )}
        </div>

        <div className="flex justify-between">
          <button
            onClick={handleReset}
            className="px-4 py-2 text-gray-600 bg-gray-200 rounded-md hover:bg-gray-300"
          >
            Réinitialiser
          </button>
          <div className="space-x-2">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-600 bg-gray-200 rounded-md hover:bg-gray-300"
            >
              Annuler
            </button>
            <button
              onClick={handleApply}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Appliquer les filtres
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

const UserRoleManager = ({ isOpen, onClose, currentUser, onUpdateUser }) => {
  const [selectedRole, setSelectedRole] = useState(currentUser?.role || 'USER');
  const [customPermissions, setCustomPermissions] = useState(currentUser?.permissions || []);

  const handleRoleChange = (role) => {
    setSelectedRole(role);
    setCustomPermissions(USER_ROLES[role].permissions);
  };

  const handlePermissionToggle = (permission) => {
    setCustomPermissions(prev => 
      prev.includes(permission) 
        ? prev.filter(p => p !== permission)
        : [...prev, permission]
    );
  };

  const handleSave = () => {
    onUpdateUser({ role: selectedRole, permissions: customPermissions });
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Gestion des Rôles Utilisateur</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-2xl">✕</button>
        </div>

        <div className="space-y-6">
          {/* Role Selection */}
          <div>
            <h3 className="text-lg font-semibold mb-3">Rôle</h3>
            <div className="space-y-2">
              {Object.entries(USER_ROLES).map(([key, role]) => (
                <label key={key} className="flex items-center">
                  <input
                    type="radio"
                    name="role"
                    value={key}
                    checked={selectedRole === key}
                    onChange={() => handleRoleChange(key)}
                    className="mr-2"
                  />
                  <span className="font-medium">{role.label}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Permissions */}
          <div>
            <h3 className="text-lg font-semibold mb-3">Permissions</h3>
            <div className="grid grid-cols-2 gap-2">
              {[
                { key: 'create', label: 'Créer' },
                { key: 'read', label: 'Lire' },
                { key: 'update', label: 'Modifier' },
                { key: 'delete', label: 'Supprimer' },
                { key: 'manage_users', label: 'Gérer utilisateurs' },
                { key: 'view_all', label: 'Voir tout' },
                { key: 'view_own', label: 'Voir ses données' },
                { key: 'export', label: 'Exporter' },
                { key: 'import', label: 'Importer' },
                { key: 'manage_config', label: 'Gérer config' }
              ].map(perm => (
                <label key={perm.key} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={customPermissions.includes(perm.key)}
                    onChange={() => handlePermissionToggle(perm.key)}
                    className="mr-2"
                  />
                  {perm.label}
                </label>
              ))}
            </div>
          </div>
        </div>

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

const BulkActionsBar = ({ selectedItems, onBulkDelete, onBulkTransition, onBulkExport, partnerType }) => {
  if (selectedItems.length === 0) return null;

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4 flex items-center justify-between">
      <span className="text-blue-800 font-medium">
        {selectedItems.length} élément{selectedItems.length > 1 ? 's' : ''} sélectionné{selectedItems.length > 1 ? 's' : ''}
      </span>
      <div className="flex space-x-2">
        <button
          onClick={onBulkExport}
          className="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700"
        >
          📊 Exporter
        </button>
        {partnerType === 'sourcing' && (
          <button
            onClick={onBulkTransition}
            className="px-3 py-1 bg-purple-600 text-white rounded text-sm hover:bg-purple-700"
          >
            ➡️ Vers Dealflow
          </button>
        )}
        <button
          onClick={onBulkDelete}
          className="px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700"
        >
          🗑️ Supprimer
        </button>
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

const StartupCard = ({ partner, type, isSelected, onSelect, onEdit, onTimeline, onComments, onDocs, onTransition }) => {
  const name = partner.nom_entreprise || partner.nom;
  const description = partner.objet || partner.actions_commentaires || "Aucune description.";
  
  // 1. AJOUT : Cette fonction définit quelle couleur utiliser pour chaque statut
  const getStatusColor = (status) => {
    const mapping = {
      "A traiter": "bg-yellow-100 text-yellow-800",
      "Clos": "bg-red-100 text-red-800",
      "Dealflow": "bg-green-100 text-green-800",
      "En cours avec les métiers": "bg-blue-100 text-blue-800",
      "En cours avec l'équipe inno": "bg-green-100 text-green-800",
      "Klaxoon": "bg-blue-100 text-blue-800"
    };
    return mapping[status] || "bg-gray-100 text-gray-800"; // Gris par défaut si inconnu
  };

  return (
    <div className={`startup-card ${isSelected ? 'ring-2 ring-blue-500' : ''}`} onClick={() => onSelect(partner.id)}>
      <div className="flex justify-between items-start">
        {/* 2. MODIFICATION : On utilise getStatusColor(partner.statut) au lieu de bg-blue-100 */}
        <span className={`card-badge ${getStatusColor(partner.statut)}`}>
          {partner.statut}
        </span>
        <input type="checkbox" checked={isSelected} readOnly className="rounded" />
      </div>

      <div className="flex items-center space-x-3 mb-3">
        <div className="w-10 h-10 bg-gray-100 rounded flex items-center justify-center font-bold text-gray-400 border">
          {name ? name[0] : "?"}
        </div>
        <h3 className="font-bold text-gray-900 truncate">{name}</h3>
      </div>

      <p className="text-gray-600 text-sm mb-4 line-clamp-3 flex-1">{description}</p>

      <div className="flex flex-wrap gap-1 mb-4">
        {partner.domaine_activite && <span className="text-[10px] bg-gray-100 px-2 py-0.5 rounded">{partner.domaine_activite}</span>}
        {partner.typologie && <span className="text-[10px] bg-purple-50 text-purple-600 px-2 py-0.5 rounded">{partner.typologie}</span>}
      </div>

      <div className="flex gap-2 pt-3 border-t border-gray-100">
        <button onClick={(e) => {e.stopPropagation(); onEdit(partner)}} className="text-xs text-blue-600 hover:underline">Modifier</button>
        <button onClick={(e) => {e.stopPropagation(); onTimeline(partner, type)}} className="text-xs text-orange-600 hover:underline">Timeline</button>
        <button onClick={(e) => {e.stopPropagation(); onDocs(partner, type)}} className="text-xs text-blue-400 hover:underline">Docs</button>
        {type === 'sourcing' && (
          <button onClick={(e) => {e.stopPropagation(); onTransition(partner.id)}} className="text-xs text-green-600 font-bold hover:underline">→ Dealflow</button>
        )}
      </div>
    </div>
  );
};

const Dashboard = () => {
  // Phase 6 - Advanced Column Filtering & Sorting State
  const [columnFilters, setColumnFilters] = useState({});
  const [columnSortConfig, setColumnSortConfig] = useState({ column: null, direction: null });

  // Phase 6 - Advanced filtering and sorting functions
  const handleColumnFilterChange = (columnKey, filterValues) => {
    setColumnFilters(prev => ({
      ...prev,
      [columnKey]: filterValues
    }));
  };

  const handleColumnSort = (columnKey, direction) => {
    setColumnSortConfig({ column: columnKey, direction });
  };

// BUG CORRIGÉ : on passe activeFilters explicitement en paramètre
  // pour éviter le problème de stale closure
  const applyAdvancedFilters = (data, currentActiveFilters = activeFilters, sort = null) => {
    let filtered = [...data];

    // Apply existing basic filters first
    filtered = applyFilters(filtered, currentActiveFilters);

    // Apply column filters
    Object.entries(columnFilters).forEach(([columnKey, filterValues]) => {
      if (filterValues && filterValues.length > 0) {
        // Handle special case: if filter contains '__NONE__', show nothing
        if (filterValues.includes('__NONE__')) {
          filtered = [];
          return;
        }
        
        filtered = filtered.filter(item => {
          const value = item[columnKey];
          let displayValue;
          
          if (value === null || value === undefined) {
            displayValue = '(Vide)';
          } else if (typeof value === 'boolean') {
            displayValue = value ? 'Oui' : 'Non';
          } else if (Array.isArray(value)) {
            displayValue = value.join(', ');
          } else {
            displayValue = String(value);
          }
          
          return filterValues.includes(displayValue);
        });
      }
    });

    // Apply sorting
    if (columnSortConfig.column && columnSortConfig.direction) {
      filtered.sort((a, b) => {
        const aVal = a[columnSortConfig.column];
        const bVal = b[columnSortConfig.column];
        
        // Handle null/undefined values
        if (aVal === null || aVal === undefined) return 1;
        if (bVal === null || bVal === undefined) return -1;
        
        // Date comparison
        if (typeof aVal === 'string' && aVal.match(/^\d{4}-\d{2}-\d{2}/)) {
          const aDate = new Date(aVal);
          const bDate = new Date(bVal);
          return columnSortConfig.direction === 'asc' ? aDate - bDate : bDate - aDate;
        }
        
        // Numeric comparison
        if (!isNaN(Number(aVal)) && !isNaN(Number(bVal))) {
          const aNum = Number(aVal);
          const bNum = Number(bVal);
          return columnSortConfig.direction === 'asc' ? aNum - bNum : bNum - aNum;
        }
        
        // String comparison
        const aStr = String(aVal).toLowerCase();
        const bStr = String(bVal).toLowerCase();
        if (columnSortConfig.direction === 'asc') {
          return aStr.localeCompare(bStr);
        } else {
          return bStr.localeCompare(aStr);
        }
      });
    }

    return filtered;
  };

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
      priorite_strategique: { visible: true, label: "Priorité" },
      score_maturite: { visible: true, label: "Maturité" },
      score_potentiel: { visible: false, label: "Potentiel" },
      tags_strategiques: { visible: false, label: "Tags" },
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
      priorite_strategique: { visible: true, label: "Priorité" },
      score_maturite: { visible: false, label: "Maturité" },
      score_potentiel: { visible: false, label: "Potentiel" },
      tags_strategiques: { visible: false, label: "Tags" },
      pilote: { visible: false, label: "Pilote" },
      typologie: { visible: false, label: "Typologie" },
      source: { visible: false, label: "Source" },
      date_reception_fichier: { visible: false, label: "Date réception" },
      date_pre_qualification: { visible: false, label: "Date pré-qualification" }
    }
  });
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
  
  // Phase 1 - Activity Timeline state
  const [showTimelineModal, setShowTimelineModal] = useState(false);
  const [selectedTimelinePartner, setSelectedTimelinePartner] = useState(null);
  
  // Phase 3 - Private Comments state
  const [showCommentsModal, setShowCommentsModal] = useState(false);
  const [selectedCommentsPartner, setSelectedCommentsPartner] = useState(null);
  
  // Phase 4 - Quick Views state
  const [showQuickViewModal, setShowQuickViewModal] = useState(false);
  const [quickViewData, setQuickViewData] = useState(null);
  
  // Phase 4 - Navigation state
  const [showHamburgerMenu, setShowHamburgerMenu] = useState(false);
  const [showQuickMenu, setShowQuickMenu] = useState(false);
  
  // Document Management state
  const [showDocumentModal, setShowDocumentModal] = useState(false);
  const [selectedPartnerForDocs, setSelectedPartnerForDocs] = useState(null);
  
  // Phase 4 - Quick Views configuration
  const quickViews = [
    { id: 'mes-startups', label: '👨‍💼 Mes Startups', color: 'purple' },
    { id: 'a-relancer', label: '⏰ À Relancer', color: 'red' },
    { id: 'avec-documents', label: '📄 Avec Docs', color: 'blue' },
    { id: 'en-experimentation', label: '🧪 En Expé', color: 'green' }
  ];
  
  const handleQuickViewSelect = (viewType) => {
    handleQuickView(viewType);
    setShowQuickMenu(false);
    setShowHamburgerMenu(false);
  };

  // Document management functions
  const handleOpenDocuments = (partner, partnerType) => {
    const partnerName = partnerType === 'sourcing' ? partner.nom_entreprise : partner.nom;
    setSelectedPartnerForDocs({
      id: partner.id,
      name: partnerName,
      type: partnerType
    });
    setShowDocumentModal(true);
  };

  const handleCloseDocuments = () => {
    setShowDocumentModal(false);
    setSelectedPartnerForDocs(null);
  };

  const fetchSourcingPartners = async () => {
    try {
      const response = await axios.get(`${API_URL}/sourcing`);
      setSourcingPartners(response.data);
      setFilteredSourcingPartners(response.data);
    } catch (error) {
      console.error("Error fetching sourcing partners:", error);
    }
  };

  const fetchDealflowPartners = async () => {
    try {
      const response = await axios.get(`${API_URL}/dealflow`);
      setDealflowPartners(response.data);
      setFilteredDealflowPartners(response.data);
    } catch (error) {
      console.error("Error fetching dealflow partners:", error);
    }
  };

  const fetchStatistics = async () => {
    try {
      const response = await axios.get(`${API_URL}/statistics`);
      setStatistics(response.data);
    } catch (error) {
      console.error("Error fetching statistics:", error);
    }
  };

  const fetchCustomFields = async () => {
    try {
      const sourcingConfig = await axios.get(`${API_URL}/config/form/sourcing`);
      const dealflowConfig = await axios.get(`${API_URL}/config/form/dealflow`);
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
      const response = await axios.get(`${API_URL}/config/columns`);
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
    console.log("🎯 HANDLECREATESOURCING - Début fonction");
    console.log("📥 Données reçues:", formData);
    console.log("🌐 API_URL:", API_URL);
    
    setLoading(true);
    try {
      console.log("🚀 Envoi POST /api/sourcing...");
      console.log("🌐 URL COMPLETE:", `${API_URL}/sourcing`);
      console.log("🌐 API_URL:", API_URL);
      console.log("🌐 BACKEND_URL:", BACKEND_URL);
      console.log("🌐 isPreview:", isPreview);
      console.log("🌐 window.location.origin:", window.location.origin);
      
      const response = await axios.post(`${API_URL}/sourcing`, formData);
      console.log("✅ POST /api/sourcing - Succès:", response.status);
      console.log("📊 Réponse:", response.data);
      
      console.log("🔄 Actualisation des données...");
      await fetchSourcingPartners();
      await fetchStatistics();
      
      console.log("✅ Fermeture du formulaire...");
      setShowSourcingForm(false);
      
      alert("✅ Partenaire créé avec succès !");
      
    } catch (error) {
      console.error("❌ ERREUR création sourcing partner:", error);
      console.error("❌ Status:", error.response?.status);
      console.error("❌ Data:", error.response?.data);
      console.error("❌ Headers:", error.response?.headers);
      
      const errorDetail = error.response?.data?.detail;
      let errorMsg = error.message || "Erreur inconnue";
      
      if (errorDetail) {
        if (Array.isArray(errorDetail)) {
          // Pydantic validation errors (array of error objects)
          const validationErrors = errorDetail.map(err => 
            `• ${err.loc ? err.loc.join('.') : 'field'}: ${err.msg}`
          ).join('\n');
          errorMsg = `Erreurs de validation :\n${validationErrors}`;
        } else if (typeof errorDetail === 'string') {
          errorMsg = errorDetail;
        } else {
          errorMsg = JSON.stringify(errorDetail, null, 2);
        }
      }
      
      alert(`❌ Erreur lors de la création (Status: ${error.response?.status}) :\n\n${errorMsg}\n\n💡 Conseil: Vérifiez que tous les champs obligatoires sont remplis correctement.`);
      console.log("📊 ERREUR COMPLÈTE:", error.response?.data);
    } finally {
      console.log("🏁 HANDLECREATESOURCING - Fin fonction");
      setLoading(false);
    }
  };

  const handleCreateDealflow = async (formData) => {
    setLoading(true);
    try {
      await axios.post(`${API_URL}/dealflow`, formData);
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
    const partnerId = editingPartner?.id || editingPartner?._id;

    if (!partnerId) {
      alert("Erreur : Identifiant du partenaire manquant.");
      return;
    }

    const baseUrl = API_URL.replace(/\/$/, "");
    // BUG CORRIGÉ : utiliser full_name qui est le bon champ du state currentUser
    const userId = encodeURIComponent(currentUser?.full_name || currentUser?.id || "default_user");
    const cleanUrl = `${baseUrl}/sourcing/${partnerId}?user_id=${userId}`;

    console.log("✅ URL finale PUT :", cleanUrl);

    await axios.put(cleanUrl, formData);

    await fetchSourcingPartners();
    await fetchStatistics();
    setEditingPartner(null);
    setShowSourcingForm(false);
    alert("✅ Modification enregistrée !");
  } catch (error) {
    console.error("Erreur détaillée modification:", error);
    alert(`La modification a échoué (Erreur ${error.response?.status}). Vérifiez la console.`);
  } finally {
    setLoading(false);
  }
};

  const handleEditDealflow = async (formData) => {
    setLoading(true);
    try {
      const partnerId = editingPartner?.id || editingPartner?._id;
      
      if (!partnerId) {
        alert("Erreur : Identifiant manquant.");
        return;
      }

      const cleanUrl = `${API_URL.replace(/\/$/, "")}/dealflow/${partnerId}`;
      await axios.put(cleanUrl, formData);
      
      await fetchDealflowPartners();
      await fetchStatistics();
      setEditingPartner(null);
      setShowDealflowForm(false);
      alert("✅ Modification enregistrée !");
    } catch (error) {
      console.error("Erreur détaillée modification:", error);
      alert("Erreur lors de la modification du Dealflow.");
    } finally {
      setLoading(false);
    }
  };
  
  const handleDeleteSourcing = async (id) => {
    if (window.confirm("Êtes-vous sûr de vouloir supprimer ce partenaire ?")) {
      try {
        await axios.delete(`${API_URL}/sourcing/${id}`);
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
        await axios.delete(`${API_URL}/dealflow/${id}`);
        await fetchDealflowPartners();
        await fetchStatistics();
      } catch (error) {
        console.error("Error deleting dealflow partner:", error);
      }
    }
  };

  // Phase 1 - Timeline functions
  const handleShowTimeline = (partner, partnerType) => {
    setSelectedTimelinePartner({
      id: partner.id,
      name: partnerType === 'sourcing' ? partner.nom_entreprise : partner.nom,
      type: partnerType
    });
    setShowTimelineModal(true);
  };

  const handleCloseTimeline = () => {
    setShowTimelineModal(false);
    setSelectedTimelinePartner(null);
  };

  // Phase 1 - Update partner after next action date change
  const handlePartnerUpdate = (updatedPartner, partnerType) => {
    if (partnerType === 'sourcing') {
      setSourcingPartners(prev => prev.map(p => p.id === updatedPartner.id ? updatedPartner : p));
    } else {
      setDealflowPartners(prev => prev.map(p => p.id === updatedPartner.id ? updatedPartner : p));
    }
  };

  // Phase 3 - Comments functions
  const handleShowComments = (partner, partnerType) => {
    setSelectedCommentsPartner({
      id: partner.id,
      name: partnerType === 'sourcing' ? partner.nom_entreprise : partner.nom,
      type: partnerType
    });
    setShowCommentsModal(true);
  };

  const handleCloseComments = () => {
    setShowCommentsModal(false);
    setSelectedCommentsPartner(null);
  };

  // Phase 4 - Quick view functions
  const handleGlobalSearch = async (query) => {
    try {
      const response = await axios.get(`${API_URL}/global-search?query=${encodeURIComponent(query)}&user_id=default_user`);
      setQuickViewData({
        view_name: `Recherche: "${query}"`,
        description: `Résultats de recherche pour "${query}"`,
        ...response.data
      });
      setShowQuickViewModal(true);
    } catch (error) {
      console.error("Error during global search:", error);
    }
  };

  const handleQuickView = async (viewType) => {
    try {
      const response = await axios.get(`${API_URL}/quick-views/${viewType}?user_id=default_user`);
      setQuickViewData(response.data);
      setShowQuickViewModal(true);
    } catch (error) {
      console.error("Error loading quick view:", error);
    }
  };

  const handleCloseQuickView = () => {
    setShowQuickViewModal(false);
    setQuickViewData(null);
  };

  const handleTransitionToDealflow = async (sourcingId) => {
    const dealflowData = {
      statut: "En cours avec l'équipe inno",
      metiers_concernes: "À définir",
      date_reception_fichier: new Date().toISOString().split('T')[0]
    };

    try {
      await axios.post(`${API_URL}/transition/${sourcingId}`, dealflowData);
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
      const response = await axios.post(`${API_URL}/enrich/${partnerId}?partner_type=${partnerType}`);
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
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [showUserRoleManager, setShowUserRoleManager] = useState(false);
  const [activeFilters, setActiveFilters] = useState({});
  const [selectedItems, setSelectedItems] = useState([]);
  const [currentUser, setCurrentUser] = useState({
    role: 'ADMIN',
    permissions: USER_ROLES.ADMIN.permissions
  });

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

  const applyFilters = (data, filters) => {
    if (!filters || Object.keys(filters).length === 0) return data;
    
    return data.filter(item => {
      // Domaine filter
      if (filters.domaine && item.domaine_activite !== filters.domaine && item.domaine !== filters.domaine) {
        return false;
      }
      
      // Statut filter  
      if (filters.statut && item.statut !== filters.statut) {
        return false;
      }
      
      // Typologie filter
      if (filters.typologie && item.typologie !== filters.typologie) {
        return false;
      }
      
      // Pays filter
      if (filters.pays && item.pays_origine !== filters.pays) {
        return false;
      }
      
      // Source filter
      if (filters.source && item.source !== filters.source) {
        return false;
      }
      
      // Pilote filter
      if (filters.pilote && !item.pilote.toLowerCase().includes(filters.pilote.toLowerCase())) {
        return false;
      }
      
      // Date range filter
      if (filters.date_debut || filters.date_fin) {
        const itemDate = new Date(item.date_entree_sourcing || item.date_reception_fichier);
        if (filters.date_debut && itemDate < new Date(filters.date_debut)) {
          return false;
        }
        if (filters.date_fin && itemDate > new Date(filters.date_fin)) {
          return false;
        }
      }
      
      // Interet filter (sourcing only)
      if (filters.interet !== "" && String(item.interet) !== filters.interet) {
        return false;
      }
      
      return true;
    });
  };

  const handleApplyFilters = (filters) => {
    setActiveFilters(filters);
    if (activeTab === 'sourcing') {
      setFilteredSourcingPartners(applyFilters(sourcingPartners, filters));
    } else if (activeTab === 'dealflow') {
      setFilteredDealflowPartners(applyFilters(dealflowPartners, filters));
    }
  };

  const handleSelectItem = (id) => {
    setSelectedItems(prev => 
      prev.includes(id) 
        ? prev.filter(item => item !== id)
        : [...prev, id]
    );
  };

  const handleSelectAll = (items) => {
    if (selectedItems.length === items.length) {
      setSelectedItems([]);
    } else {
      setSelectedItems(items.map(item => item.id));
    }
  };

  const handleBulkDelete = async () => {
    if (!window.confirm(`Êtes-vous sûr de vouloir supprimer ${selectedItems.length} éléments ?`)) {
      return;
    }
    
    try {
      const endpoint = activeTab === 'sourcing' ? '/api/sourcing' : '/api/dealflow';
      await Promise.all(
        selectedItems.map(id => axios.delete(`${API_URL}${endpoint}/${id}`))
      );
      
      // Refresh data
      if (activeTab === 'sourcing') {
        await fetchSourcingPartners();
      } else {
        await fetchDealflowPartners();
      }
      
      setSelectedItems([]);
      alert('Éléments supprimés avec succès');
    } catch (error) {
      alert('Erreur lors de la suppression');
    }
  };

  const handleBulkTransition = async () => {
    if (!window.confirm(`Transférer ${selectedItems.length} partenaires vers le dealflow ?`)) {
      return;
    }
    
    try {
      await Promise.all(
        selectedItems.map(id => 
          axios.post(`${API_URL}/transition/${id}`, {
            statut: "En cours avec l'équipe inno",
            metiers_concernes: "À définir",
            date_reception_fichier: new Date().toISOString().split('T')[0]
          })
        )
      );
      
      await fetchSourcingPartners();
      await fetchDealflowPartners();
      setSelectedItems([]);
      alert('Partenaires transférés avec succès');
    } catch (error) {
      alert('Erreur lors du transfert');
    }
  };

  const handleBulkExport = () => {
    const data = activeTab === 'sourcing' 
      ? sourcingPartners.filter(p => selectedItems.includes(p.id))
      : dealflowPartners.filter(p => selectedItems.includes(p.id));
    
    const csv = convertToCSV(data);
    downloadCSV(csv, `${activeTab}_export_${new Date().toISOString().split('T')[0]}.csv`);
  };

  const handleGlobalExport = () => {
    // Export ALL filtered data, not just selected items
    const data = activeTab === 'sourcing' 
      ? filteredSourcingPartners 
      : filteredDealflowPartners;
    
    const csv = convertToCSV(data);
    downloadCSV(csv, `${activeTab}_export_global_${new Date().toISOString().split('T')[0]}.csv`);
  };

  const convertToCSV = (data) => {
    if (data.length === 0) return '';
    
    // Define clean column mapping for both sourcing and dealflow
    const getSourcingColumns = () => ({
      'nom_entreprise': 'Nom Entreprise',
      'statut': 'Statut',
      'domaine_activite': 'Domaine d\'Activité',
      'typologie': 'Typologie',
      'pays_origine': 'Pays d\'Origine',
      'pilote': 'Pilote',
      'source': 'Source',
      'date_entree_sourcing': 'Date Entrée Sourcing',
      'interet': 'Intérêt',
      'objet': 'Objet',
      'cas_usage': 'Cas d\'Usage',
      'technologie': 'Technologie',
      'score_maturite': 'Score Maturité',
      'priorite_strategique': 'Priorité Stratégique',
      'date_prochaine_action': 'Prochaine Action',
      'actions_commentaires': 'Actions & Commentaires'
    });

    const getDealflowColumns = () => ({
      'nom': 'Nom Startup',
      'statut': 'Statut',
      'domaine': 'Domaine',
      'typologie': 'Typologie',
      'pilote': 'Pilote',
      'source': 'Source',
      'metiers_concernes': 'Métiers Concernés',
      'objet': 'Objet',
      'date_reception_fichier': 'Date Réception',
      'date_pre_qualification': 'Date Pré-qualification',
      'date_presentation_metiers': 'Date Présentation Métiers',
      'date_go_metier_etude': 'Date Go Métier Étude',
      'date_go_experimentation': 'Date Go Expérimentation',
      'date_go_generalisation': 'Date Go Généralisation',
      'date_cloture': 'Date Clôture',
      'date_prochaine_action': 'Prochaine Action',
      'actions_commentaires': 'Actions & Commentaires'
    });

    // Determine data type and get appropriate columns
    const isSourceData = data[0]?.nom_entreprise !== undefined;
    const columnMapping = isSourceData ? getSourcingColumns() : getDealflowColumns();
    
    // Format data cleanly
    const formatValue = (value) => {
      if (value === null || value === undefined) return '';
      if (typeof value === 'boolean') return value ? 'Oui' : 'Non';
      if (Array.isArray(value)) return value.join('; ');
      if (typeof value === 'object') return JSON.stringify(value);
      if (typeof value === 'string') {
        // Clean and format dates
        if (value.match(/^\d{4}-\d{2}-\d{2}/)) {
          try {
            return new Date(value).toLocaleDateString('fr-FR');
          } catch {
            return value;
          }
        }
        // Escape commas and quotes
        if (value.includes(',') || value.includes('"')) {
          return `"${value.replace(/"/g, '""')}"`;
        }
        return value;
      }
      return String(value);
    };
    
    // Create CSV content
    const headers = Object.values(columnMapping);
    const csvRows = [
      headers.join(','),
      ...data.map(row => 
        Object.keys(columnMapping).map(key => 
          formatValue(row[key])
        ).join(',')
      )
    ];
    
    return csvRows.join('\n');
  };

  const downloadCSV = (csv, filename) => {
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const hasPermission = (permission) => {
    return currentUser.permissions.includes(permission);
  };

  // Update filtered data when original data or filters change
  useEffect(() => {
    const newFilteredSourcing = applyAdvancedFilters(sourcingPartners);
    setFilteredSourcingPartners(newFilteredSourcing);
  }, [sourcingPartners, activeFilters, columnFilters, columnSortConfig]);

  useEffect(() => {
    const newFilteredDealflow = applyAdvancedFilters(dealflowPartners);
    setFilteredDealflowPartners(newFilteredDealflow);
  }, [dealflowPartners, activeFilters, columnFilters, columnSortConfig]);

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
    
    // Phase 1 - Inactivity Indicator
    if (key === 'is_inactive') {
      return <InactivityIndicator isInactive={partner.is_inactive} daysSinceUpdate={partner.days_since_update} />;
    }
    
    // Phase 1 - Next Action Date
    if (key === 'date_prochaine_action') {
      const partnerType = partner.nom_entreprise ? 'sourcing' : 'dealflow';
      return (
        <NextActionDate 
          date={value} 
          onUpdate={(updatedPartner) => handlePartnerUpdate(updatedPartner, partnerType)}
          partnerId={partner.id}
          partnerType={partnerType}
        />
      );
    }
    
    if (key === 'priorite_strategique') {
      return <PriorityTag priority={value} />;
    }
    
    if (key === 'score_maturite') {
      return <ScoreDisplay score={value} type="maturite" />;
    }
    
    if (key === 'score_potentiel') {
      return <ScoreDisplay score={value} type="potentiel" />;
    }
    
    if (key === 'tags_strategiques') {
      return <StrategicTags tags={value} />;
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
    <div className="bg-white border-b border-surm-border shadow-sm">
      <div className="max-w-[1600px] mx-auto px-6 py-4">
        <div className="flex items-center justify-between gap-6">
          {/* Bloc gauche : titre */}
          <div className="min-w-[220px]">
            <h1 className="text-2xl font-bold text-surm-navy leading-tight">
              SURM
            </h1>
            <p className="text-sm font-semibold text-surm-navy leading-tight">
              Dashboard
            </p>
          </div>

          {/* Bloc centre : recherche + vues */}
          <div className="flex items-center gap-3 flex-1 justify-center">
            <GlobalSearchBar
              onSearch={handleGlobalSearch}
              onQuickView={handleQuickView}
            />
          </div>

          {/* Bloc droite : navigation + user */}
          <div className="flex items-center gap-3">
            <nav className="hidden xl:flex items-center gap-2">
              <button
                onClick={() => setActiveTab("dashboard")}
                className={`px-4 py-2 rounded-xl text-sm font-medium flex items-center space-x-2 transition ${
                  activeTab === "dashboard"
                    ? "bg-surm-pink/10 text-surm-navy"
                    : "text-gray-600 hover:bg-gray-100"
                }`}
              >
                <span>📊</span>
                <span>Dashboard</span>
              </button>

              <button
                onClick={() => setActiveTab("kanban")}
                className={`px-4 py-2 rounded-xl text-sm font-medium flex items-center space-x-2 transition ${
                  activeTab === "kanban"
                    ? "bg-orange-100 text-orange-700"
                    : "text-gray-600 hover:bg-gray-100"
                }`}
              >
                <span>📋</span>
                <span>Kanban</span>
              </button>

              <button
                onClick={() => setActiveTab("sourcing")}
                className={`px-4 py-2 rounded-xl text-sm font-medium flex items-center space-x-2 transition ${
                  activeTab === "sourcing"
                    ? "bg-surm-pink/10 text-surm-navy"
                    : "text-gray-600 hover:bg-gray-100"
                }`}
              >
                <span>🔎</span>
                <span>Sourcing</span>
              </button>

              <button
                onClick={() => setActiveTab("dealflow")}
                className={`px-4 py-2 rounded-xl text-sm font-medium flex items-center space-x-2 transition ${
                  activeTab === "dealflow"
                    ? "bg-green-100 text-green-700"
                    : "text-gray-600 hover:bg-gray-100"
                }`}
              >
                <span>🔁</span>
                <span>Dealflow</span>
              </button>
            </nav>

            <div className="flex items-center gap-3">
              <div className="hidden lg:flex items-center bg-gray-100 rounded-xl px-3 py-2">
                <span className="text-xs text-gray-600 mr-2">
                  {USER_ROLES[currentUser.role]?.label}
                </span>
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              </div>

              <div className="relative">
                <button
                  onClick={() => setShowHamburgerMenu(!showHamburgerMenu)}
                  className="px-3 py-2 text-gray-600 bg-gray-100 rounded-xl hover:bg-gray-200 flex items-center space-x-2"
                >
                  <span>☰</span>
                  <span className="hidden lg:inline text-sm">Plus</span>
                </button>

                {showHamburgerMenu && (
                  <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-lg border border-surm-border z-50">
                    <div className="py-2">
                      <div className="px-4 py-1 text-xs font-medium text-gray-400 uppercase tracking-wide">
                        Vues Rapides
                      </div>

                      <button
                        onClick={() => {
                          setActiveTab("my-startups");
                          setShowHamburgerMenu(false);
                        }}
                        className="w-full text-left px-4 py-2 hover:bg-gray-50 flex items-center space-x-2 text-sm"
                      >
                        <span>🌟</span>
                        <span>Mes Startups</span>
                      </button>

                      <div className="relative">
                        <button
                          onClick={() => setShowQuickMenu(!showQuickMenu)}
                          className="w-full text-left px-4 py-2 hover:bg-gray-50 flex items-center justify-between text-sm"
                        >
                          <div className="flex items-center space-x-2">
                            <span>⚡</span>
                            <span>Vues</span>
                          </div>
                          <span
                            className={`text-xs transition-transform ${
                              showQuickMenu ? "rotate-90" : ""
                            }`}
                          >
                            ›
                          </span>
                        </button>

                        {showQuickMenu && (
                          <div className="ml-6 border-l border-gray-200 pl-2">
                            {quickViews.map((view) => (
                              <button
                                key={view.id}
                                onClick={() => {
                                  handleQuickViewSelect(view.id);
                                  setShowHamburgerMenu(false);
                                  setShowQuickMenu(false);
                                }}
                                className="w-full text-left px-2 py-1 hover:bg-gray-50 text-xs text-gray-600"
                              >
                                {view.label}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>

                      <hr className="my-2" />

                      <div className="px-4 py-1 text-xs font-medium text-gray-400 uppercase tracking-wide">
                        Rapports
                      </div>
                      <button
                        onClick={() => {
                          setActiveTab("reports");
                          setShowHamburgerMenu(false);
                        }}
                        className="w-full text-left px-4 py-2 hover:bg-gray-50 flex items-center space-x-2 text-sm"
                      >
                        <span>📑</span>
                        <span>Rapports</span>
                      </button>

                      <hr className="my-2" />

                      <div className="px-4 py-1 text-xs font-medium text-gray-400 uppercase tracking-wide">
                        Administration
                      </div>

                      {hasPermission("manage_config") && (
                        <button
                          onClick={() => {
                            setShowSettings(true);
                            setShowHamburgerMenu(false);
                          }}
                          className="w-full text-left px-4 py-2 hover:bg-gray-50 flex items-center space-x-2 text-sm"
                        >
                          <span>⚙️</span>
                          <span>Paramètres</span>
                        </button>
                      )}

                      {hasPermission("manage_users") && (
                        <button
                          onClick={() => {
                            setShowUserRoleManager(true);
                            setShowHamburgerMenu(false);
                          }}
                          className="w-full text-left px-4 py-2 hover:bg-gray-50 flex items-center space-x-2 text-sm"
                        >
                          <span>👥</span>
                          <span>Rôles</span>
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Navigation mobile */}
        <div className="xl:hidden border-t border-surm-border mt-4 pt-3">
          <div className="flex space-x-2 overflow-x-auto pb-1">
            <button
              onClick={() => setActiveTab("dashboard")}
              className={`px-3 py-2 rounded-xl text-xs font-medium whitespace-nowrap ${
                activeTab === "dashboard"
                  ? "bg-surm-pink/10 text-surm-navy"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              📊 Dashboard
            </button>

            <button
              onClick={() => setActiveTab("kanban")}
              className={`px-3 py-2 rounded-xl text-xs font-medium whitespace-nowrap ${
                activeTab === "kanban"
                  ? "bg-orange-100 text-orange-700"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              📋 Kanban
            </button>

            <button
              onClick={() => setActiveTab("sourcing")}
              className={`px-3 py-2 rounded-xl text-xs font-medium whitespace-nowrap ${
                activeTab === "sourcing"
                  ? "bg-surm-pink/10 text-surm-navy"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              🔎 Sourcing
            </button>

            <button
              onClick={() => setActiveTab("dealflow")}
              className={`px-3 py-2 rounded-xl text-xs font-medium whitespace-nowrap ${
                activeTab === "dealflow"
                  ? "bg-green-100 text-green-700"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              🔁 Dealflow
            </button>
          </div>
        </div>
      </div>
    </div>

    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === "kanban" && (
          <KanbanBoard isVisible={true} />
        )}

        {activeTab === "reports" && (
          <SyntheticReports isVisible={true} />
        )}

        {activeTab === "my-startups" && (
          <PersonalDashboard isVisible={true} currentUser={currentUser} />
        )}

        {activeTab === "dashboard" && (
          <div className="space-y-6">
            {/* Phase 2 - Enhanced Analytics Dashboard */}
            <AnalyticsDashboard isVisible={true} />
            
            {/* Original Statistics (kept for reference) */}
            {statistics && (
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
          </div>
        )}

        {activeTab === "sourcing" && (
  <div className="space-y-6">

    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <h2 className="text-2xl font-bold text-gray-900">Partenaires Sourcing</h2>

      <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto">

        <div className="flex gap-2">
          <button
            onClick={() => setShowAdvancedFilters(true)}
            className="px-3 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 text-sm"
          >
            🔍 Filtres
          </button>

          {hasPermission('export') && (
            <button
              onClick={() => handleGlobalExport()}
              className="px-3 py-2 bg-green-100 text-green-700 rounded-md hover:bg-green-200 text-sm"
            >
              📊 Export
            </button>
          )}
        </div>

        <div className="w-full sm:w-80">
          <SearchBar
            onSearch={(term) => handleSearch(term, 'sourcing')}
            placeholder="Rechercher dans sourcing..."
          />
        </div>

        {hasPermission('create') && (
          <button
            onClick={() => setShowSourcingForm(true)}
            className="bg-surm-pink text-white px-4 py-2 rounded-xl hover:bg-surm-pinkDark whitespace-nowrap"
          >
            Nouveau Partenaire
          </button>
        )}

      </div>
    </div>

    <BulkActionsBar
      selectedItems={selectedItems}
      onBulkDelete={handleBulkDelete}
      onBulkTransition={handleBulkTransition}
      onBulkExport={handleBulkExport}
      partnerType="sourcing"
    />

    <div className="bg-white border border-surm-border rounded-xl shadow-card p-4">

      <div className="startup-grid">
        {filteredSourcingPartners.map((partner) => (
          <StartupCard
            key={partner.id}
            partner={partner}
            type="sourcing"
            isSelected={selectedItems.includes(partner.id)}
            onSelect={handleSelectItem}
            onEdit={(p) => {
              setEditingPartner(p);
              setShowSourcingForm(true);
            }}
            onTimeline={handleShowTimeline}
            onComments={handleShowComments}
            onDocs={handleOpenDocuments}
            onTransition={handleTransitionToDealflow}
          />
        ))}
      </div>

      {filteredSourcingPartners.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">
            Aucun partenaire sourcing trouvé.
          </p>
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
                <div className="flex gap-2">
                  <button
                    onClick={() => setShowAdvancedFilters(true)}
                    className="px-3 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 text-sm"
                  >
                    🔍 Filtres
                  </button>
                  {hasPermission('export') && (
                    <button
                      onClick={() => handleGlobalExport()}
                      className="px-3 py-2 bg-green-100 text-green-700 rounded-md hover:bg-green-200 text-sm"
                    >
                      📊 Export
                    </button>
                  )}
                </div>
                <div className="w-full sm:w-80">
                  <SearchBar 
                    onSearch={(term) => handleSearch(term, 'dealflow')}
                    placeholder="Rechercher dans dealflow..."
                  />
                </div>
                {hasPermission('create') && (
                  <button
                    onClick={() => setShowDealflowForm(true)}
                    className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 whitespace-nowrap"
                  >
                    Nouveau Partenaire
                  </button>
                )}
              </div>
            </div>

            <BulkActionsBar
              selectedItems={selectedItems}
              onBulkDelete={handleBulkDelete}
              onBulkTransition={null}
              onBulkExport={handleBulkExport}
              partnerType="dealflow"
            />
            
            <EnhancedTableContainer 
              tableId="dealflow-table" 
              title="Table Dealflow"
            >
              <div className="startup-grid">
  {filteredDealflowPartners.map((partner) => (
    <StartupCard 
      key={partner.id} 
      partner={partner}
      type="dealflow"
      isSelected={selectedItems.includes(partner.id)}
      onSelect={handleSelectItem}
      onEdit={(p) => { setEditingPartner(p); setShowDealflowForm(true); }}
      onTimeline={handleShowTimeline}
      onComments={handleShowComments}
      onDocs={handleOpenDocuments}
    />
  ))}
</div>
              
              {filteredDealflowPartners.length === 0 && (
                <div className="text-center py-12">
                  <p className="text-gray-500">Aucun partenaire dealflow trouvé.</p>
                </div>
              )}
            </EnhancedTableContainer>
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
          onChangeTab={setActiveTab}
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
          onChangeTab={setActiveTab}
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

      {showAdvancedFilters && (
        <AdvancedFilters
          isOpen={showAdvancedFilters}
          onClose={() => setShowAdvancedFilters(false)}
          onApplyFilters={handleApplyFilters}
          filterType={activeTab}
        />
      )}

      {showUserRoleManager && (
        <UserRoleManager
          isOpen={showUserRoleManager}
          onClose={() => setShowUserRoleManager(false)}
          currentUser={currentUser}
          onUpdateUser={setCurrentUser}
        />
      )}

      {/* Phase 4 - Quick View Results Modal */}
      <QuickViewResults
        isVisible={showQuickViewModal}
        viewData={quickViewData}
        onClose={handleCloseQuickView}
      />

      {/* Phase 3 - Private Comments Modal */}
      {showCommentsModal && selectedCommentsPartner && (
        <PrivateCommentsModal
          isOpen={showCommentsModal}
          onClose={handleCloseComments}
          partnerId={selectedCommentsPartner.id}
          partnerType={selectedCommentsPartner.type}
          partnerName={selectedCommentsPartner.name}
        />
      )}

      {/* Phase 1 - Activity Timeline Modal */}
      {showTimelineModal && selectedTimelinePartner && (
        <ActivityTimelineModal
          isOpen={showTimelineModal}
          onClose={handleCloseTimeline}
          partnerId={selectedTimelinePartner.id}
          partnerType={selectedTimelinePartner.type}
          partnerName={selectedTimelinePartner.name}
        />
      )}

      {/* Document Management Modal */}
      {showDocumentModal && selectedPartnerForDocs && (
        <DocumentModal
          isOpen={showDocumentModal}
          onClose={handleCloseDocuments}
          partnerId={selectedPartnerForDocs.id}
          partnerType={selectedPartnerForDocs.type}
          partnerName={selectedPartnerForDocs.name}
        />
      )}
    </div>
  );
};

const DocumentModal = ({ isOpen, onClose, partnerId, partnerType, partnerName }) => {
  const [activeTab, setActiveTab] = useState('upload');
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadDocuments = async () => {
    if (!partnerId) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/documents/${partnerId}`);
      setDocuments(response.data);
    } catch (error) {
      console.error('Error loading documents:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen && partnerId) {
      loadDocuments();
    }
  }, [isOpen, partnerId]);

  const handleDocumentUploaded = (newDocument) => {
    setDocuments(prev => [newDocument, ...prev]);
    setActiveTab('list'); // Switch to list view after upload
  };

  const handleDocumentDeleted = (deletedId) => {
    setDocuments(prev => prev.filter(doc => doc.id !== deletedId));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              📂 Documents - {partnerName}
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Gestion des documents et pièces jointes
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
          >
            ✕
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b">
          <button
            onClick={() => setActiveTab('upload')}
            className={`px-6 py-3 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'upload'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            📤 Ajouter un document
          </button>
          <button
            onClick={() => setActiveTab('list')}
            className={`px-6 py-3 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'list'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            📋 Documents ({documents.length})
          </button>
        </div>

        {/* Content */}
        <div className="p-6 max-h-[70vh] overflow-y-auto">
          {activeTab === 'upload' && (
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Ajouter un nouveau document
              </h3>
              <DocumentUpload
                partnerId={partnerId}
                partnerType={partnerType}
                onDocumentUploaded={handleDocumentUploaded}
              />
            </div>
          )}

          {activeTab === 'list' && (
            <div>
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  Documents attachés ({documents.length})
                </h3>
                <button
                  onClick={loadDocuments}
                  className="text-blue-600 hover:text-blue-800 text-sm flex items-center space-x-1"
                  disabled={loading}
                >
                  <span>🔄</span>
                  <span>{loading ? 'Actualisation...' : 'Actualiser'}</span>
                </button>
              </div>
              
              {loading ? (
                <div className="text-center py-8">
                  <div className="text-2xl mb-2">⏳</div>
                  <div className="text-gray-500">Chargement des documents...</div>
                </div>
              ) : (
                <DocumentList
                  partnerId={partnerId}
                  documents={documents}
                  onDeleteDocument={handleDocumentDeleted}
                  onRefreshDocuments={loadDocuments}
                />
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end p-6 border-t bg-gray-50">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
          >
            Fermer
          </button>
        </div>
      </div>
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
