import { Routes } from '@angular/router';
import { Dashboard } from './dashboard/dashboard';
import { Simulateur } from './simulateur/simulateur';
import { Indice } from './indice/indice';

export const routes: Routes = [
    { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
    { path: 'dashboard', component: Dashboard },
    {path:'simulateur', component: Simulateur},
    {path:'indice',component: Indice},
    {path: '**', redirectTo: 'dashboard' }
];