import React, { useState } from "react";
import "../general.scss";
import { Navbar } from "./navbar";
import { Sidebar } from "./sidebar";
// import swal from 'sweetalert';

const API = process.env.REACT_APP_API;

export const NewFlow = () =>{

    const [rulesList, setRulesList] = useState(['load_source_main']);
    const [paramsList, setParamsList] = useState({});
    const [page, setPage] = useState(0);

    // const handleSubmit = async (e) => {

    //     e.preventDefault();

    //     const form = new FormData();
    //     form.append('dataSource', file);
    //     form.append('pName', projectName);
    //     form.append('fileType', fileType);
    //     form.append('sep', sep);
    //     form.append('enc', enc);

    //     console.log(URL.createObjectURL(file))

    //     const res = await fetch(API + '/addProject/' + localStorage.getItem('email'),{
    //         method: 'POST',
    //         headers:{
    //             "Access-Control-Allow-Origin": "*"
    //         },
    //         body: form
    //     });

    //     const data = await res.json();

    //     if(res.status !== 200 && data.msg !== ''){
    //         swal({
    //             title: 'Error al cargar la fuente de datos',
    //             text: 'Revise de nuevo los campos.',
    //             icon: 'error',
    //             button: 'Volver a intentarlo',
    //             confirmButtonColor: "#000",
    //             timer: "10000"
    //         });

    //         setFile('');
    //         setProjectName('');
    //         setFileType('');
    //         setSep('');
    //         setEnc('');

    //     }else{
    //         swal({
    //             title: 'Carga exitosa',
    //             text: data.msg + ' : ' + data.objID,
    //             icon: 'success',
    //             button: 'Continuar',
    //             confirmButtonColor: "#000",
    //             timer: "10000"
    //         })

    //         setFile('');
    //         setProjectName('');
    //         setFileType('');
    //         setSep('');
    //         setEnc('');
    //     }
        
    // }

    const availableRules = [
        {
            id: 1,
            name: "Guardar cambios",
            value: "save_source_main",
            desc: "Guarda los cambios realizados al proyecto.",
            params: [
                {
                    name: 'param1',
                    type: 'file'
                },
                {
                    name: 'param2',
                    type: 'text'
                },
                {
                    name: 'param3',
                    type: 'text'
                },

            ]
        },
        {
            id: 2,
            name: "Aplicar sinónimo",
            value: "apply_synonymous",
            desc: "Aplica una sustitución de sinónimos a la columna.",
            params: [
                {
                    name: 'param4',
                    type: 'file'
                },
                {
                    name: 'param5',
                    type: 'text'
                },
                {
                    name: 'param6',
                    type: 'text'
                },

            ]
        },
        {
            id: 3,
            name: "Validar existencia en catálogo",
            value: "validate_exist_in_catalog",
            desc: "Comprobar si el registro existe en un catálogo.",
            params: [
                {
                    name: 'param7',
                    type: 'file'
                },
                {
                    name: 'param8',
                    type: 'text'
                },
                {
                    name: 'param9',
                    type: 'text'
                },

            ]
        },
        {
            id: 4,
            name: "Validar fonético",
            value: "validar_fonetico",
            desc: "Aplicar el algoritmo soundex en la columna deseada.",
            params: [
                {
                    name: 'param10',
                    type: 'file'
                },
                {
                    name: 'param11',
                    type: 'text'
                },

            ]
        },
    ];

    const extractParams = () => {

        const extractedParams = [];

        for ( let i=0 ; i < availableRules.length ; i++) {
            if (rulesList.includes(availableRules[i].value)){
                extractedParams.push(availableRules[i].params)
            }
        }

        // console.log(extractedParams)

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

    console.log(paramsList)

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
                            <div className="col">
                                <input type="checkbox" value={'load_source_main'} checked disabled /> <span className="ruletitle">Cargar proyecto</span>
                                <p className="ruledesc">Lorem ipsum dolor sit amet consectetur adipisicing elit. Fuga, odit!</p>
                            </div>

                            {
                                availableRules.map((item, index) => (
                                    <div className="col" key={index}>
                                        <input type="checkbox" value={item.value} onChange={handleChange} /> <span className="ruletitle">{item.name}</span>
                                        <p className="ruledesc">{item.desc}</p>
                                    </div>
                                ))
                            }

                            <div className="col">
                                <input type="checkbox" value={'save_source_main'} checked disabled /> <span className="ruletitle">Guardar cambios</span>
                                <p className="ruledesc">Lorem ipsum dolor sit amet consectetur adipisicing elit. Fuga, odit!</p>
                            </div>
                            <div className="changebuttons">
                                <button disabled={page === 0}>Anterior</button>
                                <button onClick={() => {setPage((page) => page + 1)}}>Siguiente</button>
                            </div>
                        </div>
                    ) : (
                            <div className="bottom flow">

                                {
                                    extractedParams.map(item => (
                                        item.map((param, index) => (
                                            <div className="col" key={index}>
                                                <p>{param.name}</p>
                                                <input onChange={handleParamChange} name={param.name} type={param.type} />
                                            </div>
                                        ))
                                    ))
                                }

                                <div className="changebuttons">
                                    <button onClick={() => {setPage((page) => page - 1)}}>Anterior</button>
                                    <button disabled={page === titles.length - 1} onClick={() => {setPage((page) => page + 1)}}>Siguiente</button>
                                </div>
                            </div>
                    )
                }
            </div>
        </div>
    )
}