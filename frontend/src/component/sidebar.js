import React from "react";
import "../general.scss"
import DashboardIcon from '@mui/icons-material/Dashboard';
import InventoryIcon from '@mui/icons-material/Inventory';
import PersonIcon from '@mui/icons-material/Person';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import HelpIcon from '@mui/icons-material/Help';
import EmailIcon from '@mui/icons-material/Email';
import FileUploadIcon from '@mui/icons-material/FileUpload';
import DownloadIcon from '@mui/icons-material/Download';

export const Sidebar = () =>{
  return (
    <div className="sidebar">
        <div className="top">
          <span className="logo">DataHub</span>
        </div>
        <hr></hr>
        <div className="center">
          <ul>
            <p className="title">MAIN</p>
            <li>
              <DashboardIcon className="icon"/>
              <span>Dashboard</span>
            </li>
            <li>
              <PersonIcon className="icon"/>
              <span>Mi Cuenta</span>
            </li>
            <li>
              <InventoryIcon className="icon"/>
              <span>Repositorio</span>
            </li>
            <p className="title">PROCESOS</p>
            <li>
              <FileUploadIcon className="icon"/>
              <span>Importar</span>
            </li>
            <li>
              <AccountTreeIcon className="icon"/>
              <span>Flujos</span>
            </li>
            <li>
              <DownloadIcon className="icon"/>
              <span>Exportar</span>
            </li>
            <p className="title">AYUDA</p>
            <li>
              <HelpIcon className="icon"/>
              <span>FAQ</span>
            </li>
            <li>
              <EmailIcon className="icon"/>
              <span>Contáctanos</span>
            </li>
          </ul>
        </div>
        <div className="bottom">options</div>
    </div>
  )
}