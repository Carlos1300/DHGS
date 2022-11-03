import React from "react";
import "../general.scss"
import { Sidebar } from "./sidebar";

export const Dashboard = () =>{
    return (
        <div className="home">
            <Sidebar />
            <div className="homeContainer">container</div>
        </div>
    )
}