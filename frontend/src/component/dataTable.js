import React from "react";
import "../general.scss";
import { DataGrid} from '@mui/x-data-grid';
import { Link } from "react-router-dom";

const columns = [
  { field: 'id', headerName: 'ID', width: 70 },
  { field: 'user', headerName: 'User', width: 330,
  renderCell: (params) =>{
    return(
      <div className="cellWithImg">
        <img className="cellImg" src={params.row.img} alt="avatar" />
        {params.row.username}
      </div>
    )
  } },
  {field: "email", headerName: "Email", width: 230},
  {field: "age", headerName: "Age", width: 100},
  {field: "status", headerName: "Status", width: 160,
  renderCell: (params) =>{
    return(
      <div className={`cellWithStatus ${params.row.status}`}>{params.row.status}</div>
    )
  }}
  // { field: 'lastName', headerName: 'Last name', width: 130 },
  // {
  //   field: 'age',
  //   headerName: 'Age',
  //   type: 'number',
  //   width: 90,
  // },
  // {
  //   field: 'fullName',
  //   headerName: 'Full name',
  //   description: 'This column has a value getter and is not sortable.',
  //   sortable: false,
  //   width: 160,
  //   // renderCell: (params) =>{
  //   //     return(HTML)
  //   // } Para renderear algún elemento HTML
  //   valueGetter: (params) =>
  //     `${params.row.firstName || ''} ${params.row.lastName || ''}`,
  // },
];

const rows = [
  { 
    id: 1, 
    username: 'Snow',
    img: 'https://f1racingsport.com/wp-content/uploads/2020/05/person-6.jpg',
    status: 'active',
    email: 'a@gmail.com',
    age: 35
  },
  { 
    id: 2, 
    username: 'Jamie Lannister', 
    img: 'https://www.theportlandclinic.com/wp-content/uploads/2019/07/Person-Curtis_4x5-e1564616444404.jpg',
    status: 'pending',
    email: 'b@gmail.com',
    age: 42
  },
  { 
    id: 3, 
    username: 'Targaryen', 
    img: 'http://siga-aluminio.com.mx/wp-content/uploads/2019/01/person4.jpg',
    status: 'passive',
    email: 'c@gmail.com',
    age: 45 
  },
  { 
    id: 4, 
    username: 'Eren', 
    img: 'https://dergreif-online.de/www/wp-content/uploads/2016/07/Timothy_hoch.jpg',
    status: 'active',
    email: 'd@gmail.com',
    age: 64 
  },
  { 
    id: 5, 
    username: 'Marcy', 
    img: 'http://siga-aluminio.com.mx/wp-content/uploads/2019/01/person5.jpg',
    status: 'passive',
    email: 'e@gmail.com',
    age: 37 
  },
  { 
    id: 6, 
    username: 'Milka', 
    img: 'https://strayhornlaw.com/wp-content/uploads/2019/09/image0-1170x1170.jpeg',
    status: 'active',
    email: 'f@gmail.com',
    age: 42 
  },
  { 
    id: 7, 
    username: 'Rita', 
    img: 'https://law.northeastern.edu/wp-content/uploads/2021/03/persons-NUSL-2015_6630.jpg',
    status: 'active',
    email: 'g@gmail.com',
    age: 42 
  },
  { 
    id: 8, 
    username: 'Mark', 
    img: 'http://siga-aluminio.com.mx/wp-content/uploads/2019/01/person6.jpg',
    status: 'passive',
    email: 'h@gmail.com',
    age: 25 
  },
  { 
    id: 9, 
    username: 'Heung', 
    img: 'https://files.mb.com.ph/wp-content/uploads/2022/10/26161615/108991.jpeg',
    status: 'passive',
    email: 'i@gmail.com',
    age: 62 
  },
  { 
    id: 10, 
    username: 'Heung', 
    img: 'https://files.mb.com.ph/wp-content/uploads/2022/10/26161615/108991.jpeg',
    status: 'passive',
    email: 'i@gmail.com',
    age: 62 
  },
];

export const DataTable = () => {

    const viewAlert = async () => {
      alert('View');
    }

    const actionColumn = [
      { field: "action", headerName: "Action", width: 200, renderCell:()=>{
        return(
          <div className="cellAction">
            <div className="viewButton" onClick={viewAlert}>View</div>
            <div className="deleteButton">Delete</div>
          </div>
        )
      }}
    ]

    return(
        <div className="datatable">
          <div className="manageTable">
            <Link to="/nuevo"><div className="addButton">Agregar Datos</div></Link>
          </div>
            <DataGrid
            rows={rows}
            columns={columns.concat(actionColumn)}
            pageSize={9}
            rowsPerPageOptions={[9]}
            checkboxSelection
            />
        </div>
    )
}