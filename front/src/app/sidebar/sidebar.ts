import { NgClass, NgIf } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  standalone: true,
  selector: 'app-sidebar',
  imports: [RouterLink,NgClass,NgIf],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.scss',
})
export class Sidebar {
 isOpen = false; // état du menu mobile

  toggle() {
    this.isOpen = !this.isOpen;
    console.log('Sidebar mobile isOpen =', this.isOpen);
  }

  close() {
    this.isOpen = false;
  }
}