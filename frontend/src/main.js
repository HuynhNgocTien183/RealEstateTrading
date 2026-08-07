import { mount } from 'svelte';
import App from './App.svelte';
import './styles/global.css';
import './styles/variable.css';

const app = mount(App, {
  target: document.getElementById('app'),
});

export default app;