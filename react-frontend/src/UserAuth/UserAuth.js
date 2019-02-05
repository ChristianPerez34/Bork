import React, {Component} from 'react';
import './UserAuth.css';
import {Button, Form, FormGroup, Input, Label} from "reactstrap";
import axios from 'axios';

export default class UserAuth extends Component {

    constructor(props) {
        super(props);
        this.state = {username: ''}
    }

    handleChange = event => {
        this.setState({username: event.target.value});
    };

    handleSubmit = event => {
        event.preventDefault();

        // const user = {
        //   username: this.state.username
        // };
        const data = new FormData();
        data.append('username', this.state.username);
        axios.post(`http://localhost:5000/api/user/1`, data, {
            headers: {'Content-Type': 'application/json',}
        })
            .then(res => {
                console.log(res);
                console.log(res.data);
            })
    };


    render() {
        // const {username, password, submitted, loading, error} = this.state;
        return (
            <div className="UserAuth">
                <Form onSubmit={this.handleSubmit} className="login">
                    <FormGroup>
                        <Label for="username">Username</Label>
                        <Input
                            type="username"
                            name="username"
                            id="username"
                            placeholder="Enter username"
                            onChange={this.handleChange}
                        />
                    </FormGroup>
                    <FormGroup>
                        <Label for="examplePassword">Password</Label>
                        <Input
                            type="password"
                            name="password"
                            id="examplePassword"
                            placeholder="Enter password"
                        />
                    </FormGroup>
                    <Button id="login-button">Login</Button>
                </Form>
            </div>
        );
    }
}
