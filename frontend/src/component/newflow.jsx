import React, { useState, useEffect } from "react";
import "../general.scss";
import { Navbar } from "./navbar";
import { Sidebar } from "./sidebar";
import swal from 'sweetalert';
import { useNavigate } from "react-router-dom";

const API = process.env.REACT_APP_API;

export const NewFlow = () =>{

    const [rulesList, setRulesList] = useState([]);
    const [paramsList, setParamsList] = useState([]);
    const [page, setPage] = useState(0);
    const [availableRules, setAvailableRules] = useState([]);
    const navigate = useNavigate();

    const getRules = async () =>{
        const res = await fetch(API + '/getRules');
        const data = await res.json();
        setAvailableRules(data);
      }
    
      useEffect(() => {
        getRules();
      }, [])

    const extractParams = () => {

        const extractedParams = [];

        for ( let i=0 ; i < availableRules.length ; i++) {
            if (rulesList.includes(availableRules[i].value)){
                extractedParams.push(availableRules[i].params)
            }
        }

        return extractedParams;
    }

    const extractedParams = extractParams();


    const handleChange = (e) =>{
        const {value, checked} = e.target;

        if(checked){
            setRulesList(pre => [...pre, value]);
        }else{
            setRulesList(pre => {
                return [...pre.filter(rule => rule!==value)];
            })
        }
    }

    const handleParamChange = (e) => {
        if (e.target.type === 'file'){
            let updatedValue = {}
            updatedValue = {[e.target.name]: e.target.files[0]}

            setParamsList(paramsList => ({
                ...paramsList,
                ...updatedValue
                
            }))
        } else {
            let updatedValue = {}
            updatedValue = {[e.target.name]: e.target.value}

            setParamsList(paramsList => ({
                ...paramsList,
                ...updatedValue
                
            }))
        }
    }

    const handleSubmit = async (e) => {

        e.preventDefault();

        const JSONdata = [];

        let JSONelement = {};

        JSONdata.push({...{
            dispname: "Cargar fuente",
            order: 0,
            name: "load_source_main"
        }})

        let order = 1;

        if(rulesList.length !== 0 && paramsList.length !== 0){ 
            for (const rule of availableRules.map(a => a)){
                if (rulesList.includes(rule.value)){
                    JSONelement.dispname = rule.name
                    JSONelement.name = rule.value
                    JSONelement.order = order;
                    order++;
                    for(const param of rule.params.map(a => a.name)){
                        JSONelement[param] = paramsList[param];
                    }

                    JSONdata.push({...JSONelement})
                }

                for (const prop of Object.getOwnPropertyNames(JSONelement)) {
                    delete JSONelement[prop];
                }
            }
        }

        JSONdata.push({...{
            dispname: "Guardar Datos",
            order: order++,
            name: "save_source_main",
            collection: "DataCleaned"
        }})
            
        const res = await fetch(API + '/addFlow/' + localStorage.getItem('email'),{
            method: 'POST',
            headers:{
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            body: JSON.stringify(JSONdata),
        });

        const data = await res.json();

        if(res.status !== 200 && data.msg !== ''){
            swal({
                title: 'Error al cargar la fuente de datos',
                text: 'Revise de nuevo los campos.',
                icon: 'error',
                button: 'Volver a intentarlo',
                confirmButtonColor: "#000",
                timer: "10000"
            });

            setRulesList([]);
            setParamsList([]);

        }else{
            swal({
                title: 'Carga exitosa',
                text: data.msg,
                icon: 'success',
                button: 'Continuar',
                confirmButtonColor: "#000",
                timer: "10000"
            })

            navigate('/flows')
            setRulesList([]);
            setParamsList([]);
        }
        
    }

    const titles = ['Agregar Reglas', 'Agregar Parámetros']

    return(
        <div className="new">
            <Sidebar />
            <div className="newContainer">
                <Navbar />
                <div className="top">
                    <h1 className="title">{titles[page]}</h1>
                </div>
                {
                    page === 0 ? (

                        <div className="bottom flow">

                            {
                                availableRules.map((item, index) => (
                                    <div className="col" key={index}>
                                        <input type="checkbox" value={item.value} onChange={handleChange} /> <span className="ruletitle">{item.name}</span>
                                        <p className="ruledesc">{item.desc}</p>
                                    </div>
                                ))
                            }

                            <div className="changebuttons">
                                <button onClick={() => {setPage((page) => page + 1); extractParams()}}>Siguiente</button>
                            </div>
                        </div>
                    ) : (
                            <div className="bottom flow">

                                {
                                    extractedParams.length !== 0 ? (

                                        extractedParams.map(item => (
                                            item.map((param, index) => (
                                                param.name !== 'None' ? (
                                                    <div className="col" key={index}>
                                                        <p className="displayName">{param.display_name}</p>
                                                        <input className="parambox" placeholder={param.desc} onChange={handleParamChange} name={param.name} type={param.type} required/>
                                                    </div>
                                                ) : (
                                                    <></>
                                                )
                                            ))
                                        ))
                                    ) : (
                                        <div className="col warn" style={{justifyContent: "center"}}>
                                            <p className="warning">¡Ninguna regla seleccionada!</p>
                                        </div>
                                    )

                                }

                                <div className="changebuttons">
                                    <button onClick={() => {setPage((page) => page - 1); setParamsList([]);}}>Anterior</button>
                                    <button disabled={extractedParams.length === 0} onClick={handleSubmit}>Añadir</button>
                                </div>
                            </div>
                    )
                }
            </div>
        </div>
    )
}