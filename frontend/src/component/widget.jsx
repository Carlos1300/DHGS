import React, { useState, useEffect } from "react";
import "../general.scss";
import InventoryIcon from '@mui/icons-material/Inventory';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import AppsIcon from '@mui/icons-material/Apps';
import { Link } from "react-router-dom";

const API = process.env.REACT_APP_API;

export const Widget = ({ type }) =>{
    const [count, setCount] = useState([])

    const getCountData = async () => {
        const res = await fetch(API + '/dashboard_info/' + localStorage.getItem('email'));
        const res_json = await res.json();
        setCount(res_json);
    }
    
    useEffect(() => {
        getCountData();
    }, []);

    let data;

    switch(type){
        case "users":
            data={
                title: "PROYECTOS",
                isMoney: false,
                link: "Mi Repositorio",
                icon: <InventoryIcon className="icon" />,
                linkTo: '/repo',
                amount: count[0]
            };
            break;
        case "order":
            data={
                title: "CATALOGOS",
                isMoney: false,
                link: "Mis Catálogos",
                icon: <MenuBookIcon className="icon" />,
                linkTo: '/flows',
                amount: 0
            };
            break;
        case "earnings":
            data={
                title: "FLUJOS",
                link: "Mis Flujos",
                icon: <AccountTreeIcon className="icon" />,
                linkTo: '/flows',
                amount: count[1]
            };
            break;
        case "balance":
            data={
                title: "REGLAS",
                icon: <AppsIcon className="icon" />,
                amount: count[2]
            };
            break;
        default:
            break;
    }

    return(
        <div className="widget">
            <div className="left">
                <span className="title">{data.title}</span>
                <span className="counter">{data.isMoney && "$"} {data.amount}</span>
                <span className="link"><Link to={data.linkTo}>{data.link}</Link></span>
            </div>
            <div className="right">
                {data.icon}
            </div>
        </div>
    )
}