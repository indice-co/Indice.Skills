---
name: angular-conventions
description: >
  Use when writing or reviewing Angular code at Indice: standalone components vs.
  modules, folder structure, state management, RxJS patterns, change detection,
  and styling conventions. Prefer Indice.Angular components before building new UI.
---

# Angular conventions

## Purpose
Company-wide UI standard for Angular applications. Read this before creating or
changing Angular code.

These rules describe new code on Angular 20 and later. In an existing app, match the
version and patterns already there and migrate only what you were asked to change.

## Guardrail
Before building a new component, directive, or service, check
[Indice.Angular](https://github.com/indice-co/Indice.Angular) for an existing one,
and say what you checked.

## Standalone components vs. modules
- New apps bootstrap with `bootstrapApplication(App, appConfig)`. Providers live in
  `app.config.ts` and routes in `app.routes.ts`. Do not create NgModules.
- New components, directives, and pipes are standalone and list what they use in `imports`.
- Use `input()`, `output()`, `model()`, and signal queries (`viewChild()`, `contentChild()`),
  not the decorators.
- Use built-in control flow (`@if`, `@for` with `track`, `@switch`), not `*ngIf` / `*ngFor`.
- Inject with `inject()` into `private readonly` fields. Write new guards and interceptors
  as functions (`CanActivateFn`, `HttpInterceptorFn`).
- In an NgModule-based app, add to the existing feature module the way its neighbours do.
  A library that only ships a module is wired with `importProvidersFrom(...)`.

## Folder structure
```text
src/app/
  app.config.ts
  app.routes.ts
  core/              # app-wide infrastructure, loaded once
    auth/            # guards, interceptors, callback pages
    layout/          # shell, navigation
    models/          # settings and other app-wide types
    services/        # generated API clients (beside their .nswag file), stores
  shared/            # reusable UI used by two or more features; no API calls
  features/
    <feature>/
      <feature>-page.component.ts     # routed page: loads data, owns the screen state
      <name>.component.ts             # focused pieces used by the page
      <feature>.models.ts             # view models and mappers
```
- A feature never imports from another feature. Move what both need to `shared/` or `core/`.
- `shared/` never imports from `features/`.
- Keep a component in its feature until a second feature needs it.
- Lazy-load feature routes with `loadComponent` / `loadChildren`.
- One class per file. Name files `<name>.component.ts`, `<name>.service.ts`,
  `<name>.store.ts`, `<name>.guard.ts`, `<name>.interceptor.ts`.

## State management
Indice apps do not use a store library (NgRx, NGXS, Akita). Do not add one.

- **Component state** lives in `signal()` fields on the component. Derive with `computed()`;
  never store a value that can be computed.
- **State shared across routes** lives in a store: a `providedIn: 'root'` service that exposes
  signals and the methods that change them. Components read the signals and call the
  methods; they never `set` a store signal directly.
- **Server data** is owned by the server. Load it, show it, and reload after a command
  succeeds. Do not keep a client copy that can drift, and do not mark an action successful
  before the server confirms it.
- **List state** (page, page size, sort, search, filters) lives in the query string so a
  screen survives refresh and back navigation. `BaseListComponent` does this.
- Model async screens as three signals: the data, `loading`, and `failed` (or an error).
- Use `effect()` only to sync with something outside Angular (storage, the DOM, a third-party
  widget). Do not use it to copy one signal into another.

## RxJS patterns
- Observables are for HTTP calls and event streams. Signals are for state. Convert at the
  component or store boundary with `toSignal()` or `subscribe` + `set`.
- End every manual subscription with `takeUntilDestroyed(this.destroyRef)`. Do not keep
  `Subscription` fields and `ngOnDestroy` cleanup, except to cancel a request that a newer
  one supersedes.
- Never subscribe inside a subscribe. Compose with `switchMap` (latest wins: search, route
  params), `concatMap` (ordered writes), `exhaustMap` (ignore repeat submits), or `forkJoin`
  (parallel loads).
- Debounce user-typed search (300 ms, 3 characters minimum) and use `distinctUntilChanged()`.
- Handle errors where the user can be told: set the `failed` signal or show a toast. Do not
  swallow them with an empty `catchError`.
- Suffix observable fields with `$` (`user$`). Do not suffix signals.

## Change detection
- Every component is OnPush. From Angular 22 that is the default; before 22, set
  `changeDetection: ChangeDetectionStrategy.OnPush` explicitly.
- New apps are zoneless: `provideZonelessChangeDetection()` and no `zone.js`.
- Do not set `ChangeDetectionStrategy.Eager` (or `Default`) on new components. Leave it on
  existing components that have it.
- State that the template reads is a signal, an input, or goes through the `async` pipe.
  A plain field assigned in a callback does not update the view.
- Replace arrays and objects instead of mutating them: `list.update(l => [...l, item])`.
- Do not call `detectChanges()`. Use `markForCheck()` only in code that cannot use a signal.
- Do not call functions that compute or allocate from a template; use `computed()` or a pipe.

## Styling
- Tailwind CSS utility classes in the template are the default. Check the app's Tailwind
  major version before writing config: v4 is configured in CSS (`@import "tailwindcss"`,
  `@theme`, `@source`, `@plugin`), v3 in `tailwind.config.js`.
- Brand colours, fonts, and spacing are design tokens in `@theme` in the global `styles.css`.
  Use the token class (`bg-primary`), not a hex value or arbitrary value (`bg-[#f27731]`).
- When the same long class list repeats, extract a component. Use `@apply` in
  `@layer components` in `styles.css` only for small shared primitives such as buttons.
- Add a component stylesheet only for what utilities cannot express. No inline `style`
  attributes, no `::ng-deep`, no `!important`.
- Use the component library the app already has. New back-office apps start from
  `@indice/ng-components` and import its stylesheet into the global `styles.css`.
- Build class names from complete strings. Tailwind cannot see `'text-' + color`.

## Examples
A store that shares state across routes:
```ts
@Injectable({ providedIn: 'root' })
export class CasesStore {
  private readonly api = inject(CasesApiService);
  private readonly destroyRef = inject(DestroyRef);

  readonly cases = signal<CaseSummary[]>([]);
  readonly loading = signal(false);
  readonly activeId = signal<string | null>(null);
  readonly active = computed(() => this.cases().find(c => c.id === this.activeId()) ?? null);

  refresh(): void {
    this.loading.set(true);
    this.api.getCases().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: result => { this.cases.set(result.items ?? []); this.loading.set(false); },
      error: () => this.loading.set(false)
    });
  }

  select(id: string): void {
    this.activeId.set(id);
  }
}
```

A routed page that loads its own data:
```ts
@Component({
  selector: 'app-case-page',
  imports: [SkeletonLoaderComponent],
  templateUrl: './case-page.component.html'
})
export class CasePageComponent {
  private readonly api = inject(CasesApiService);
  private readonly destroyRef = inject(DestroyRef);

  readonly id = input.required<string>();        // route parameter, via withComponentInputBinding()

  protected readonly details = signal<CaseDetails | null>(null);
  protected readonly loading = signal(true);
  protected readonly failed = signal(false);
  protected readonly canApprove = computed(() => this.details()?.allowedActions?.approve ?? false);

  constructor() {
    toObservable(this.id).pipe(
      tap(() => { this.loading.set(true); this.failed.set(false); }),
      switchMap(id => this.api.getCase(id).pipe(catchError(() => { this.failed.set(true); return of(null); }))),
      takeUntilDestroyed(this.destroyRef)
    ).subscribe(result => { this.details.set(result); this.loading.set(false); });
  }
}
```

```html
@if (loading()) {
  <lib-skeleton-loader type="table" />
} @else if (failed()) {
  <p class="text-sm text-red-700">The case could not be loaded.</p>
} @else {
  <h1 class="text-xl font-semibold">{{ details()?.title }}</h1>
  @for (note of details()?.notes; track note.id) {
    <p class="mt-2 text-sm text-gray-700">{{ note.text }}</p>
  } @empty {
    <p class="text-sm text-gray-500">No notes yet.</p>
  }
}
```
