import React from "react";
import "../general.scss";
import { ProjectFlows } from "./projectFlows";
import { Navbar } from "./navbar";
import { Sidebar } from "./sidebar";

export const ListProjectFlows = () =>{
    return(
        <div className="list">
            <Sidebar />
            <div className="listContainer">
                <Navbar />
                <ProjectFlows />
            </div>
        </div>
    )
}