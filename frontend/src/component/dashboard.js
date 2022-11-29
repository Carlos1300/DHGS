import React from "react";
import "../general.scss";
import { Sidebar } from "./sidebar";
import { Navbar } from "./navbar";
import { Widget } from "./widget";
import { Featured } from "./featured";
import { Chart } from "./chart";
import { TableUI } from "./table";

export const Dashboard = () =>{
    return (
        <div className="home">
            <Sidebar />
            <div className="homeContainer">
                <Navbar />
                <div className="widgets">
                    <Widget type="users"/>
                    <Widget type="order"/>
                    <Widget type="earnings"/>
                    <Widget type="balance"/>
                </div>
                <div className="charts">
                    <Featured />
                    <Chart aspect={2 / 1} title="Last 6 Months (Revenue)"/>
                </div>
                <div className="listContainer">
                    <div className="listTitle">Latest Transactions</div>
                    <TableUI />
                </div>
            </div>
        </div>
    )
}