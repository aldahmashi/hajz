import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { REPO_URL } from '../core/links';

@Component({
  selector: 'app-header',
  imports: [RouterLink],
  template: `
    <header class="bg-black text-white">
      <nav class="container-page flex h-16 items-center justify-between" aria-label="Main">
        <a routerLink="/" class="flex items-baseline gap-2" aria-label="Hajz home">
          <span class="font-display text-2xl font-medium tracking-tight">Hajz</span>
          <span class="text-on-dark-mute text-lg" lang="ar">حجز</span>
        </a>
        <a class="btn-outline-dark h-10 px-5 text-sm" [href]="repoUrl" target="_blank" rel="noopener">
          View on GitHub
        </a>
      </nav>
    </header>
  `,
})
export class Header {
  protected readonly repoUrl = REPO_URL;
}
