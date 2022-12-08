import React, { useContext } from "react";
import "../general.scss";
import SearchIcon from '@mui/icons-material/Search';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import WorkOffIcon from '@mui/icons-material/WorkOff';
import WorkIcon from '@mui/icons-material/Work';
import { ProjectContext } from "../context/projectContext";

export const Navbar = () =>{

  const activeProject = useContext(ProjectContext);

  return (
    <div className="mynavbar">
      <div className="wrapper">
        <div className="search">
          <input type="text" placeholder="Buscar..."/>
          <SearchIcon className="icon" />
        </div>
        <div className="items">

          {
            activeProject[0] === 'None' ? (
              <div className="item">
                <WorkOffIcon className="icon" style={{color: "red"}}/>
                &nbsp; Ningún proyecto activo
              </div>
            ) : (
              <div className="item">
                <WorkIcon className="icon" style={{color: "limegreen"}}/>
                &nbsp; Proyecto activo: {activeProject[0]}
              </div>
            )
          }
          
          <div className="item">
            <DarkModeIcon className="icon" />
          </div>
          <div className="item">
            <img src="https://www.intus.com.mx/wp-content/uploads/2017/04/INTUS-3.png" alt="logo" className="avatar"/>
          </div>
        </div>
      </div>
    </div>
  )
}