import React from "react";
import "../general.scss";
import SearchIcon from '@mui/icons-material/Search';
import TranslateIcon from '@mui/icons-material/Translate';
import DarkModeIcon from '@mui/icons-material/DarkMode';

export const Navbar = () =>{
  return (
    <div className="mynavbar">
      <div className="wrapper">
        <div className="search">
          <input type="text" placeholder="Buscar..."/>
          <SearchIcon className="icon" />
        </div>
        <div className="items">
          <div className="item">
            <TranslateIcon className="icon" />
            Español
          </div>
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