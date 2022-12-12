import React from "react";
import "../general.scss";
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import PersonIcon from '@mui/icons-material/Person';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import MonetizationOnIcon from '@mui/icons-material/MonetizationOn';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import { Link } from "react-router-dom";

export const Widget = ({ type }) =>{

    let data;

    const amount= 100;
    const diff = 20;

    switch(type){
        case "users":
            data={
                title: "PROYECTOS",
                isMoney: false,
                link: "Mi Repositorio",
                icon: <PersonIcon className="icon" />,
                linkTo: '/repo'
            };
            break;
        case "order":
            data={
                title: "ORDERS",
                isMoney: false,
                link: "View all orders",
                icon: <ShoppingCartIcon className="icon" />,
                linkTo: '/repo'
            };
            break;
        case "earnings":
            data={
                title: "EARNINGS",
                isMoney: true,
                link: "View net earnings",
                icon: <MonetizationOnIcon className="icon" />,
                linkTo: '/repo'
            };
            break;
        case "balance":
            data={
                title: "BALANCE",
                isMoney: true,
                link: "See details",
                icon: <AccountBalanceWalletIcon className="icon" />,
                linkTo: '/repo'
            };
            break;
        default:
            break;
    }

    return(
        <div className="widget">
            <div className="left">
                <span className="title">{data.title}</span>
                <span className="counter">{data.isMoney && "$"} {amount}</span>
                <span className="link"><Link to={data.linkTo}>{data.link}</Link></span>
            </div>
            <div className="right">
                <div className="percentage positive">
                    <KeyboardArrowUpIcon />
                    {diff}%
                </div>
                {data.icon}
            </div>
        </div>
    )
}