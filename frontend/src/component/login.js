import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import swal from 'sweetalert';


const API = process.env.REACT_APP_API;

export const Login = () => {

    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleClick = async () =>{
        const res = await fetch(API + '/',
        {
            method: 'POST',
            headers:{
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email,
                password
            })
        })

        const data = await res.json();

        if(res.status !== 200 && data.msg !== ''){
            swal({
                title: 'Error al iniciar sesión',
                text: data.msg,
                icon: 'error',
                button: 'Volver a intentarlo',
                confirmButtonColor: "#000",
                timer: "10000"
            });
            setEmail('');
            setPassword('');
        }else{
            localStorage.setItem('name', data.name);
            localStorage.setItem('address', data.address);
            localStorage.setItem('country', data.country);
            localStorage.setItem('email', data.email);
            localStorage.setItem('tel', data.tel);
            localStorage.setItem('token', data.token);
            navigate('dashboard')
        }
    }

    return(
        <section className="h-100 gradient-form" style={{backgroundColor: '#eee'}}>
            <div className="container py-4 h-100">
                <div className="row d-flex justify-content-center align-items-center h-100">
                    <div className="col-xl-10">
                        <div className="card rounded-3 text-black">
                            <div className="row g-0 rounded">
                                <div className="col-lg-6 rounded-start">
                                    <div className="card-body p-md-5 mx-md-4">
                                        <div className="text-center">
                                            <img src="https://www.intus.com.mx/wp-content/uploads/2017/04/INTUS-3.png" alt="logo" style={{width: 185, padding: 10, marginBottom: 10}}/>
                                        </div>
                                        <form>
                                            <p style={{fontSize: 20}}>Ingresa a tu cuenta</p>
                                            <div className="form-outline mb-4">
                                                <input className="form-control" type="email" placeholder="Ingrese su correo" id="emailInput" onChange={e => setEmail(e.target.value)} value={email}/>
                                            </div>
                                            <div className="form-outline mb-4">
                                                <input className="form-control" type="password" id="passInput" placeholder="Ingrese su contraseña" onChange={e => setPassword(e.target.value)} value={password}/>
                                            </div>
                                            <div className="text-center pt-1 mb-5 pb-1">
                                                <div className="d-grip gap-2 col-6 mx-auto">
                                                    <button className="btn btn-primary mb-3 rounded" type="button" style={{backgroundColor: "#18615B", borderColor: "#18615B"}} onClick={handleClick}>
                                                        Ingresar
                                                    </button>
                                                </div>
                                                <Link className="text-muted" to="/about">¿Olvidaste tu contraseña?</Link>
                                            </div>
                                            <div className="d-flex align-items-center justify-content-center pb-4">
                                                <p className="mb-0 me-2">¿Aún no tienes cuenta?</p>
                                                <button type="button" className="btn btn-outline-primary">¡Date de alta!</button>
                                            </div>
                                        </form>
                                    </div>
                                </div>
                                <div className="col-lg-6 d-flex align-items-center rounded-end" style={{backgroundImage: "linear-gradient(135deg, rgba(0,140,106,1) 50%, rgba(2,198,159,1) 100%)"}}>
                                    <div className="text-white px-3 py-4 p-md-5 mx-md-4">
                                        <h4 className="mb-4">Bienvenido a nuestro DataHub</h4>
                                        <p className="small mb-0">Con nuestra plataforma podrás almacenar, transformar, perfilar y aumentar la información que tengas dentro de una base de datos. Además, podrás exportarla a donde tu desees.</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    )
}