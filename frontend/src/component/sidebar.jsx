import React, { useContext } from "react";
import "../general.scss"
import DashboardIcon from '@mui/icons-material/Dashboard';
import InventoryIcon from '@mui/icons-material/Inventory';
import PersonIcon from '@mui/icons-material/Person';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import HelpIcon from '@mui/icons-material/Help';
import EmailIcon from '@mui/icons-material/Email';
import FileUploadIcon from '@mui/icons-material/FileUpload';
import DownloadIcon from '@mui/icons-material/Download';
import LogoutIcon from '@mui/icons-material/Logout';
import HistoryIcon from '@mui/icons-material/History';
import { Link } from "react-router-dom";
import { ProjectContext } from "../context/projectContext";
import CleaningServicesIcon from '@mui/icons-material/CleaningServices';
import DatasetIcon from '@mui/icons-material/Dataset';

export const Sidebar = () => {

  const [activeProject, setActiveProject] = useContext(ProjectContext);

  const logout = async () => {
    localStorage.removeItem('name');
    localStorage.removeItem('address');
    localStorage.removeItem('country');
    localStorage.removeItem('email');
    localStorage.removeItem('tel');
    localStorage.removeItem('token');
    localStorage.removeItem('project');
    setActiveProject('None')
  }

  return (
    <div className="sidebar">
        <div className="top">
          <Link to='/dashboard'>
            <span className="logo" style={{textDecoration: "none"}}>DataHub</span>
          </Link>
        </div>
        <hr></hr>
        <div className="center">
          <ul>
            <p className="title">PRINCIPAL</p>
            <Link to="/dashboard">
              <li>
                <DashboardIcon className="icon"/>
                <span>Dashboard</span>
              </li>
            </Link>
            <Link to="/cuenta">
            <li>
              <PersonIcon className="icon"/>
              <span>Mi Cuenta</span>
            </li>
            </Link>
            <Link to="/repo">
              <li>
                <InventoryIcon className="icon"/>
                <span>Repositorio</span>
              </li>
            </Link>
            <p className="title">PROCESOS</p>
            <Link to="/nuevo">
            <li>
              <FileUploadIcon className="icon"/>
              <span>Importar</span>
            </li>
            </Link>
            <li>
              <AccountTreeIcon className="icon"/>
              <span>Flujos</span>
            </li>
            <li>
              <DownloadIcon className="icon"/>
              <span>Exportar</span>
            </li>
              {
                activeProject !== 'None' ? (
                  <div>
                    <p className="title">HERRAMIENTAS DE PROYECTO</p>
                    <Link to= '/dataperf'>
                      <li>
                        <DatasetIcon className="icon"/>
                        <span>Datos Perfilados</span>
                      </li>
                    </Link>
                    <li>
                      <CleaningServicesIcon className="icon"/>
                      <span>Datos Procesados</span>
                    </li>
                    <Link to= '/dataloads'>
                      <li>
                        <HistoryIcon className="icon"/>
                        <span>Cargas de Datos</span>
                      </li>
                    </Link>
                  </div>
                ) : (<div></div>)
                
              }
            <p className="title">AYUDA</p>
            <li>
              <HelpIcon className="icon"/>
              <span>FAQ</span>
            </li>
            <li>
              <EmailIcon className="icon"/>
              <span>Contáctanos</span>
            </li>
            <p className="title">CERRAR SESIÓN</p>
            <Link to="/">
              <li onClick={logout}>
                <LogoutIcon className="icon"/>
                <span>Salir</span>
              </li>
            </Link>
          </ul>
        </div>
    </div>
  )
}