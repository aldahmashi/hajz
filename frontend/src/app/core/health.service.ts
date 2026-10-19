import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';

/** Mirrors GET /api/health in backend/routes/health.py. */
export interface Health {
  status: 'ok';
  env: string;
  database: 'ok';
  migration: string;
}

@Injectable({ providedIn: 'root' })
export class HealthService {
  private readonly http = inject(HttpClient);

  check(): Observable<Health> {
    return this.http.get<{ data: Health }>('/api/health').pipe(map((response) => response.data));
  }
}
