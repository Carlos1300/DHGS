import React from "react";
import "../general.scss";
import { RulesTable } from "./rulesTable";
import { Navbar } from "./navbar";
import { Sidebar } from "./sidebar";

export const ListRules = () =>{
    return(
        <div className="list">
            <Sidebar />
            <div className="listContainer">
                <Navbar />
                <RulesTable />
            </div>
        </div>
    )
}