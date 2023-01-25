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
import { Link, useNavigate } from "react-router-dom";
import { ProjectContext } from "../context/projectContext";
import CleaningServicesIcon from '@mui/icons-material/CleaningServices';
import DatasetIcon from '@mui/icons-material/Dataset';
import { AuthContext } from "../context/AuthContext";
import DescriptionIcon from '@mui/icons-material/Description';

export const Sidebar = () => {

  const {dispatch} = useContext(AuthContext);

  const [activeProject, setActiveProject] = useContext(ProjectContext);

  const navigate = useNavigate();

  const logout = () => {

    dispatch({type: "LOGOUT"});
    localStorage.removeItem('name');
    localStorage.removeItem('address');
    localStorage.removeItem('country');
    localStorage.removeItem('tel');
    localStorage.removeItem('token');
    localStorage.removeItem('project');
    localStorage.removeItem('projObjID');
    setActiveProject('None');
    navigate('/');

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
            <Link to='/filemenu'>
              <li>
                <DescriptionIcon className="icon"/>
                <span>Archivos</span>
              </li>
            </Link>
            <p className="title">PROCESOS</p>
            <Link to="/nuevo">
            <li>
              <FileUploadIcon className="icon"/>
              <span>Importar</span>
            </li>
            </Link>
            <Link to='/flows'>
              <li>
                <AccountTreeIcon className="icon"/>
                <span>Flujos</span>
              </li>
            </Link>
            <Link to='/export'>
              <li>
                <DownloadIcon className="icon"/>
                <span>Exportar</span>
              </li>
            </Link>
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
                    <Link to='/export'>
                      <li>
                        <CleaningServicesIcon className="icon"/>
                        <span>Datos Procesados</span>
                      </li>
                    </Link>
                    <Link to= '/dataloads'>
                      <li>
                        <HistoryIcon className="icon"/>
                        <span>Cargas de Datos</span>
                      </li>
                    </Link>
                    <Link to= '/projectflows'>
                      <li>
                        <AccountTreeIcon className="icon"/>
                        <span>Flujos del Proyecto</span>
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
              <li onClick={logout}>
                <LogoutIcon className="icon"/>
                <span>Salir</span>
              </li>
          </ul>
        </div>
    </div>
  )
}