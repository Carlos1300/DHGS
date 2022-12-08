import React from "react";
import "../general.scss";
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import PersonIcon from '@mui/icons-material/Person';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import MonetizationOnIcon from '@mui/icons-material/MonetizationOn';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';

export const Widget = ({ type }) =>{

    let data;

    const amount= 100;
    const diff = 20;

    switch(type){
        case "users":
            data={
                title: "USERS",
                isMoney: false,
                link: "See all users",
                icon: <PersonIcon className="icon" />
            };
            break;
        case "order":
            data={
                title: "ORDERS",
                isMoney: false,
                link: "View all orders",
                icon: <ShoppingCartIcon className="icon" />
            };
            break;
        case "earnings":
            data={
                title: "EARNINGS",
                isMoney: true,
                link: "View net earnings",
                icon: <MonetizationOnIcon className="icon" />
            };
            break;
        case "balance":
            data={
                title: "BALANCE",
                isMoney: true,
                link: "See details",
                icon: <AccountBalanceWalletIcon className="icon" />
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
                <span className="link">{data.link}</span>
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