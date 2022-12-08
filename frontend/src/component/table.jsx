import React from "react";
import "../general.scss";
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';

export const TableUI = () => {

    const rows = [
        {
            id: 123456,
            product: "Papas",
            img: "https://dam.cocinafacil.com.mx/wp-content/uploads/2018/07/beneficios-de-la-papa-1.jpg",
            customer: "Abraham Gil",
            date: "Octubre 4",
            amount: 600,
            method: "Pago en efectivo",
            status: "Aprobado"
        },
        {
            id: 932012,
            product: "Durazno",
            img: "https://www.gob.mx/cms/uploads/image/file/479734/durazno1.jpg",
            customer: "Carlos Ávila",
            date: "Octubre 16",
            amount: 200,
            method: "En línea",
            status: "Aprobado"
        },
        {
            id: 115526,
            product: "Arándano",
            img: "https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/Cranberries20101210.jpg/1200px-Cranberries20101210.jpg",
            customer: "Regina Rivas",
            date: "Octubre 20",
            amount: 170,
            method: "Pago en efectivo",
            status: "Pendiente"
        },
        {
            id: 5615616,
            product: "PlayStation 5",
            img: "https://ichef.bbci.co.uk/news/640/cpsprodpb/6162/production/_114403942_ps5.jpg",
            customer: "Elisa Bonilla",
            date: "Octubre 31",
            amount: 15000,
            method: "Online",
            status: "Pendiente"
        },
        {
            id: 5615617,
            product: "Autopartes",
            img: "https://acnews.blob.core.windows.net/imgnews/medium/NAZ_383016593d904edda2e2a1c1f6b1fe3c.jpg",
            customer: "Joshua Hernández",
            date: "Noviembre 2",
            amount: 1000,
            method: "Depósito",
            status: "Aprobado"
        }

    ]



    return(
        <TableContainer component={Paper} className="table">
            <Table sx={{ minWidth: 650 }} aria-label="simple table">
                <TableHead>
                <TableRow>
                    <TableCell className="tableCell">Tracking ID</TableCell>
                    <TableCell className="tableCell">Product</TableCell>
                    <TableCell className="tableCell">Customer</TableCell>
                    <TableCell className="tableCell">Date</TableCell>
                    <TableCell className="tableCell">Amount</TableCell>
                    <TableCell className="tableCell">Payment Method</TableCell>
                    <TableCell className="tableCell">Status</TableCell>
                </TableRow>
                </TableHead>
                <TableBody>
                {rows.map((row) => (
                    <TableRow key={row.id}>
                        <TableCell className="tableCell">{row.id}</TableCell>
                        <TableCell className="tableCell">
                            <div className="cellWrapper">
                                <img src={row.img} alt="" className="image"/>
                                {row.product}
                            </div>
                        </TableCell>
                        <TableCell className="tableCell">{row.customer}</TableCell>
                        <TableCell className="tableCell">{row.date}</TableCell>
                        <TableCell className="tableCell">{row.amount}</TableCell>
                        <TableCell className="tableCell">{row.method}</TableCell>
                        <TableCell className="tableCell"><span className={`status ${row.status}`}>{row.status}</span></TableCell>
                    </TableRow>
                ))}
                </TableBody>
            </Table>
        </TableContainer>
    )
}