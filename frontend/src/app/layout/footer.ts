import { Component } from '@angular/core';

@Component({
  selector: 'app-footer',
  template: `
    <footer class="bg-black py-20 text-sm text-on-dark-mute">
      <div class="container-page flex flex-col gap-6 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p class="font-display text-xl font-medium text-white">Hajz · حجز</p>
          <p class="mt-2 max-w-md">
            A portfolio project. Listings come from Inside Airbnb; payments run in Stripe test
            mode, so no real money moves.
          </p>
        </div>
        <p>© {{ year }} Hajz</p>
      </div>
    </footer>
  `,
})
export class Footer {
  protected readonly year = new Date().getFullYear();
}
