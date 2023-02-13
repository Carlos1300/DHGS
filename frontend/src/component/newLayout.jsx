import React, { useState } from "react";
import "../general.scss";
import { Navbar } from "./navbar";
import { Sidebar } from "./sidebar";
import Swal from 'sweetalert2';

const API = process.env.REACT_APP_API;

export const NewLayout = () =>{

    const [layoutName, setLayoutName] = useState('');
    const [header, setHeader] = useState('Sí');
    const [options, setOptions] = useState([
        {colOrder: '', colName: '', colPosition: '', dataType: '', allowNull: '', aliasSource: ''},
    ]);
    const [description, setDescription] = useState('');

    const handleChangeInput = (index, event) => {
        const exValues = [...options];
        exValues[index][event.target.name] = event.target.value;
        setOptions(exValues);
    }

    const handleRuleSubmit = async () => {
        const toGoJSON = {
            layoutName: layoutName,
            header: header,
            layoutDesc: description,
            options: options
        }

        const res = await fetch(API + '/layouts/' + localStorage.getItem('project'),{
            method: 'POST',
            headers:{
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            body: JSON.stringify(toGoJSON),
        });

        const data = await res.json();

        if(res.status !== 200 && data.msg !== ''){
            Swal.fire({
                title: 'Error al agregar',
                text: data.msg,
                icon: 'error',
                button: 'Volver a intentarlo',
                confirmButtonColor: "#000",
                timer: "10000"
            });

        }else{
            Swal.fire({
                title: 'Carga exitosa',
                text: data.msg,
                icon: 'success',
                button: 'Continuar',
                confirmButtonColor: "#000",
                timer: "10000"
            })

            setLayoutName('');
            setHeader('Sí');
            setDescription('');
            setOptions([
                {colOrder: '', colName: '', colPosition: '', dataType: '', allowNull: '', aliasSource: ''}
            ]);


        }
    }

    const handleAddFields = () => {
        setOptions([...options, {colOrder: '', colName: '', colPosition: '', dataType: '', allowNull: '', aliasSource: ''}]);
    }

    const handleRemoveFields = (index) => {
        const reValues = [...options];
        reValues.splice(index, 1);
        setOptions(reValues)
    }

    return(
        <div className="new">
            <Sidebar />
            <div className="newContainer">
                <Navbar />
                <div className="top">
                    <h1 className="title">Nuevo Layout</h1>
                </div>
                <div className="top rulename">
                    <div className="ruleinfo">
                        <p className="ruletitle">Nombre</p>
                        <input className="parambox" type="text" name="flowName" value={layoutName} onChange={e => setLayoutName(e.target.value)} required placeholder="Nombre del Layout" />
                    </div>
                    <div className="ruleinfo">
                        <p className="ruletitle">Encabezado</p>
                        <select onChange={e => setHeader(e.target.value)} value={header} className="ruleselect">
                            <option value="Yes">Sí</option>
                            <option value="No">No</option>
                        </select>
                    </div>
                </div>
                <div className="top flowname">
                    <p className="ruletitle">Descripción</p>
                    <textarea value={description} onChange={e => setDescription(e.target.value)}></textarea>
                </div>

                <div className="bottom rule">
                    {
                        options.map((val, index) => (
                            <div className="ruleparams">
                                <div className="ruleinfo">
                                    <p className="ruletitle">Orden</p>
                                    <input className="parambox" type="number" name="colOrder" value={val.colOrder} onChange={e => handleChangeInput(index, e)} required placeholder="Posición deseada" />
                                </div>
                                <div className="ruleinfo">
                                    <p className="ruletitle">Nuevo nombre</p>
                                    <input className="parambox" type="text" name="colName" value={val.colName} onChange={e => handleChangeInput(index, e)} required placeholder="Nombre de columna" />
                                </div>
                                <div className="ruleinfo">
                                    <p className="ruletitle">Posición original</p>
                                    <input className="parambox" type="text" name="colPosition" value={val.colPosition} onChange={e => handleChangeInput(index, e)} required placeholder="Posición principal" />
                                </div>
                                <div className="ruleinfo">
                                    <p className="ruletitle">Tipo de dato</p>
                                    <select name="dataType" onChange={e => handleChangeInput(index, e)} value={val.dataType} className="ruleselect">
                                        <option value="TEXT">TEXT</option>
                                        <option value="NUMBER">NUMBER</option>
                                        <option value="DATE">DATE</option>
                                        <option value="ALPHANUM">ALPHANUM</option>
                                        <option value="DIGITS">DIGITS</option>
                                    </select>
                                </div>
                                <div className="ruleinfo">
                                    <p className="ruletitle">Valores Nulos</p>
                                    <select name="allowNull" onChange={e => handleChangeInput(index, e)} value={val.allowNull} className="ruleselect">
                                        <option value="No">No</option>
                                        <option value="Yes">Sí</option>
                                    </select>
                                </div>
                                <div className="ruleinfo">
                                    <p className="ruletitle">Alias</p>
                                    <input className="parambox" type="text" name="aliasSource" value={val.aliasSource} onChange={e => handleChangeInput(index, e)} required placeholder="Posibles nombres" />
                                </div>
                                <div className="dynamicButtons">
                                    <button onClick={() => handleAddFields()}>+</button>
                                    <button onClick={() => handleRemoveFields(index)}>-</button>
                                </div>
                            </div>
                        ))
                    }
                </div>
                <div className="changebuttons">
                    <button onClick={handleRuleSubmit}>Agregar</button>
                </div>

            </div>
        </div>
    )
}