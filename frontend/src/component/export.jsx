import React, { useState } from 'react'
import { Sidebar } from './sidebar';
import { Navbar } from './navbar';
// import swal from 'sweetalert';
import { utils, writeFile } from 'xlsx';

const API = process.env.REACT_APP_API;

export const Export = () => {
    const [projectName, setProjectName] = useState("");
    const [fileType, setFileType] = useState("csv");
    const [enc, setEnc] = useState("UTF-8");
    const [outputName, setOutputName] = useState("")

    const handleSubmit = async () => {

        var project = '';

        if (localStorage.getItem('project') === 'None'){
            project = projectName;
        }else{
            project = localStorage.getItem('project')
        }

        const ExportJSON = {
            projectName: project + localStorage.getItem('user'),
            fileType: fileType,
            enc: enc,
            outputName: outputName
        }

        const res = await fetch(API + '/export_data/' + localStorage.getItem('email'),{
            method: 'POST',
            headers:{
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            body: JSON.stringify(ExportJSON)
        });

        const data = await res.json();

        // console.log(data.data)

        if (data.type === 'xlsx'){
            let ws = utils.json_to_sheet(data.data.data);
            let wb = utils.book_new();
            utils.book_append_sheet(wb, ws, "Hoja1");
            writeFile(wb, data.filename);

            setProjectName('');

        } else if(data.type === 'csv'){
            const url = window.URL.createObjectURL(new Blob([data.data]));
            const link = document.createElement('a');
            link.href = url
            link.setAttribute('download', data.filename)
            document.body.appendChild(link)
            link.click()

            setProjectName('');
        }else{
            const fileData = JSON.stringify(data.data);
            const blob = new Blob([fileData], { type: "text/plain" });
            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.download = data.filename;
            link.href = url;
            link.click();

            setProjectName('');
        }
    }

    return(
        <div className="new">
            <Sidebar />
            <div className="newContainer">
                <Navbar />
                <div className="top">
                    <h1 className="title">Exportar Datos</h1>
                </div>
                <div className="bottom export">
                    {
                        localStorage.getItem('project') !== 'None' ? (
                        <></>        
                        ) : (

                            <div className="formInput">
                                <p className='ruletitle'>Nombre de Proyecto</p>
                                <input className='parambox' type="text" name="pName" value={projectName} placeholder="Nombre de proyecto" onChange={e => setProjectName(e.target.value)}/>
                            </div>
                        )
                    }
                    <div className="formInput">
                        <p className='ruletitle'>Nombre del Archivo</p>
                        <input className='parambox' type="text" name='oName' value={outputName} placeholder="Nombre del archivo" onChange={e => setOutputName(e.target.value)}/>
                    </div>
                    <div className="formInput">
                        <p className='ruletitle'>Tipo de Archivo</p>
                        <select name="fileType" onChange={e => setFileType(e.target.value)}>
                            <option value="csv" selected>CSV</option>
                            <option value="xlsx">XLSX</option>
                            <option value="txt">TXT</option>
                            <option value="json">JSON</option>
                        </select>
                    </div>
                    <div className="formInput">
                        <p className='ruletitle'>Codificación</p>
                        <select name="enc" onChange={e => setEnc(e.target.value)}>
                            <option value="UTF-8" selected>UTF-8</option>
                            <option value="ISO-8859-1">ISO-8859-1</option>
                            <option value="LATIN-1">LATIN-1</option>
                            <option value="OTRO">OTRO</option>
                        </select>
                    </div>
                </div>
                <div className='exportButton'>
                    <button className="sendButton" onClick={handleSubmit}>Exportar</button>
                </div>
            </div>
        </div>
    )
}
