import React from "react";
import "../general.scss";
import { Flows } from "./flows";
import { Navbar } from "./navbar";
import { Sidebar } from "./sidebar";

export const ListFlows = () =>{
    return(
        <div className="list">
            <Sidebar />
            <div className="listContainer">
                <Navbar />
                <Flows />
            </div>
        </div>
    )
}