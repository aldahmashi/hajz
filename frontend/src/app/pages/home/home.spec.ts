import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Home } from './home';

describe('Home', () => {
  let fixture: ComponentFixture<Home>;
  let http: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Home],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();

    fixture = TestBed.createComponent(Home);
    http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
  });

  afterEach(() => http.verify());

  const text = () => (fixture.nativeElement as HTMLElement).textContent ?? '';
  const query = (selector: string) => (fixture.nativeElement as HTMLElement).querySelector(selector);

  it('shows the API as operational when /api/health succeeds', async () => {
    http.expectOne('/api/health').flush({
      data: { status: 'ok', env: 'local', database: 'ok', migration: '0006_assistant' },
    });
    await fixture.whenStable();

    expect(query('[data-testid="status-ok"]')).toBeTruthy();
    expect(text()).toContain('0006_assistant');
  });

  it('shows the backend error message and retries on click', async () => {
    http.expectOne('/api/health').flush(
      { error: { code: 'DATABASE_UNAVAILABLE', message: 'Database is unreachable.' } },
      { status: 503, statusText: 'Service Unavailable' },
    );
    await fixture.whenStable();

    expect(query('[data-testid="status-down"]')).toBeTruthy();
    expect(text()).toContain('Database is unreachable.');

    (query('button') as HTMLButtonElement).click();
    http.expectOne('/api/health');
  });

  it('lists all 14 cities', () => {
    http.expectOne('/api/health');
    expect((fixture.nativeElement as HTMLElement).querySelectorAll('li.badge-tag').length).toBe(14);
  });
});
