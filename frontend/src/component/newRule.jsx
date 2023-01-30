import React, { useState } from "react";
import "../general.scss";
import { Navbar } from "./navbar";
import { Sidebar } from "./sidebar";
import Swal from 'sweetalert2';

const API = process.env.REACT_APP_API;

export const NewRule = () =>{

    const [ruleName, setRuleName] = useState('');
    const [ruleType, setRuleType] = useState('SINONIMO');
    const [values, setValues] = useState([
        {originalValue: '', changeValue: ''},
    ]);
    const [description, setDescription] = useState('');

    const handleChangeInput = (index, event) => {
        const exValues = [...values];
        exValues[index][event.target.name] = event.target.value;
        setValues(exValues);
    }

    const handleRuleSubmit = async () => {
        const toGoJSON = {
            ruleName: ruleName,
            ruleType: ruleType,
            ruleDesc: description,
            values: values
        }

        const res = await fetch(API + '/rules/' + localStorage.getItem('project'),{
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

            setRuleName('');
            setRuleType('SINONIMO');
            setDescription('');
            setValues([
                {originalValue: '', changeValue: ''}
            ]);


        }
    }

    const handleAddFields = () => {
        setValues([...values, {originalValue: '', changeValue: ''}]);
    }

    const handleRemoveFields = (index) => {
        const reValues = [...values];
        reValues.splice(index, 1);
        setValues(reValues)
    }

    return(
        <div className="new">
            <Sidebar />
            <div className="newContainer">
                <Navbar />
                <div className="top">
                    <h1 className="title">Nueva Regla</h1>
                </div>
                <div className="top rulename">
                    <div className="ruleinfo">
                        <p className="ruletitle">Nombre</p>
                        <input className="parambox" type="text" name="flowName" value={ruleName} onChange={e => setRuleName(e.target.value)} required placeholder="Nombre de la Regla" />
                    </div>
                    <div className="ruleinfo">
                        <p className="ruletitle">Tipo de Regla</p>
                        <select onChange={e => setRuleType(e.target.value)}   value={ruleType} className="ruleselect">
                            <option value="SINONIMO">SINÓNIMO</option>
                            <option value="RANGO NUMÉRICO">RANGO NUMÉRICO</option>
                        </select>
                    </div>
                </div>
                <div className="top flowname">
                    <p className="ruletitle">Descripción</p>
                    <textarea value={description} onChange={e => setDescription(e.target.value)}></textarea>
                </div>
        
                <div className="bottom rule">
                    {
                        values.map((val, index) => (
                            <div className="ruleparams">
                                <div className="ruleinfo">
                                    <p className="ruletitle">Valor original</p>
                                    <input className="parambox" type="text" name="originalValue" value={val.originalValue} onChange={e => handleChangeInput(index, e)} required placeholder="Valor en la tabla" />
                                </div>
                                <div className="ruleinfo">
                                    <p className="ruletitle">Valor de cambio</p>
                                    <input className="parambox" type="text" name="changeValue" value={val.changeValue} onChange={e => handleChangeInput(index, e)} required placeholder="Valor de reemplazo" />
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