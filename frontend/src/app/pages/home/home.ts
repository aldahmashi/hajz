import { HttpErrorResponse } from '@angular/common/http';
import { Component, inject, OnInit, signal } from '@angular/core';
import { Health, HealthService } from '../../core/health.service';
import { REPO_URL } from '../../core/links';

type Status =
  | { state: 'loading' }
  | { state: 'ok'; health: Health }
  | { state: 'down'; reason: string };

@Component({
  selector: 'app-home',
  templateUrl: './home.html',
})
export class Home implements OnInit {
  private readonly healthService = inject(HealthService);

  protected readonly repoUrl = REPO_URL;
  protected readonly status = signal<Status>({ state: 'loading' });

  protected readonly cities = [
    'Tokyo', 'Bangkok', 'Singapore', 'Taipei', 'Istanbul', 'London', 'Paris',
    'Barcelona', 'Rome', 'New York City', 'Mexico City', 'Rio de Janeiro', 'Cape Town', 'Sydney',
  ];

  protected readonly features = [
    {
      title: 'Ask in plain words',
      body: '“2 adults, Tokyo, quiet, near the metro, under $150” becomes real stays you can book.',
    },
    {
      title: '“Why this?”',
      body: 'Every recommendation explains itself, from what you saved, viewed and booked before.',
    },
    {
      title: 'Never double-booked',
      body: 'The database itself guarantees two guests can never hold the same night.',
    },
  ];

  ngOnInit(): void {
    this.refresh();
  }

  protected refresh(): void {
    this.status.set({ state: 'loading' });
    this.healthService.check().subscribe({
      next: (health) => this.status.set({ state: 'ok', health }),
      error: (err: HttpErrorResponse) =>
        this.status.set({
          state: 'down',
          reason: err.error?.error?.message ?? 'The API is not reachable.',
        }),
    });
  }
}
