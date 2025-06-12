# TGRAMLLM Frontend: Architecture & Guiding Principles

This document outlines the architectural decisions, design patterns, and core principles that guide the development of the TgramBuddy LLM Frontend. Its purpose is to ensure consistency, maintainability, and scalability as the project evolves and the team grows.

## Core Philosophy

Our primary goal is to build a robust, high-performance, and scalable application capable of serving a large user base. Every architectural decision is weighed against our core principles:

1.  **Clean Code:** Code is written for humans first, machines second. It must be readable, simple, and self-documenting.
2.  **Scalability & Extensibility:** The architecture must accommodate new features and increasing complexity without requiring major refactoring.
3.  **Predictability & Maintainability:** A new developer should be able to quickly understand the codebase, locate relevant files, and make changes with confidence.
4.  **Testability:** Code should be structured in a way that facilitates easy and effective unit, integration, and end-to-end testing.
5.  **Performance:** The application must remain fast and responsive, even as data volumes grow.

## Key Architectural Decisions & Rationale

### 1. Technology Stack: The "Why" Behind Our Choices

-   **TypeScript over JavaScript:** This was a foundational decision.
    -   **Rationale:** For a large-scale application, static typing is non-negotiable. TypeScript provides compile-time error checking, which eliminates entire classes of runtime bugs (e.g., `undefined is not a function`). It enhances code quality, provides superior IntelliSense for developers, and serves as a form of "living documentation," making the codebase easier to reason about and refactor safely.

-   **TanStack Query (React Query) for Server State Management:** We deliberately avoid using local state (`useState`/`useEffect`) or client-state libraries (like Redux) for managing server data.
    -   **Rationale:** TanStack Query is a specialized tool for server state. It declaratively handles caching, background refetching, loading/error states, and request deduplication. This drastically reduces boilerplate code, eliminates common bugs associated with manual data fetching, and significantly improves the user experience by providing instant feedback and keeping data fresh.

-   **TanStack Table (React Table) for Data Grids:** We chose this "headless" UI library over component-based solutions like MUI X DataGrid.
    -   **Rationale:** "Headless" means the library provides the logic (state management, sorting, filtering, pagination APIs) but gives us **100% control over the rendering**. This aligns with our principles of extensibility and performance. We can build fully custom, accessible, and highly performant tables using our own MUI components, without being locked into a specific UI implementation or needing to override styles.

-   **Vite for Build Tooling:**
    -   **Rationale:** Vite offers an exceptional developer experience (DX) with near-instant Hot Module Replacement (HMR) and significantly faster build times compared to older bundlers. Its native ES Module-based approach is modern and efficient.

### 2. Architectural Pattern: Feature-Sliced Design (FSD)

We adhere to a strict, layered architecture based on the principles of **Feature-Sliced Design (FSD)**. This is the cornerstone of our project's structure.

**FSD Layers (from lowest to highest):**

-   `src/shared`: **The Foundation.** Contains code with no project-specific logic. This includes UI-kit components (`Button`, `Input`), helper functions (`useDebounce`), API client instances (`axios`), and global configs. This layer is highly portable and could be published as an NPM package.
-   `src/entities`: **Business Entities.** Represents core business concepts like `User` or `ApiKey`. This layer typically includes data types, API hooks for interacting with the entity (`useApiKeys`), and simple components to represent the entity (`ApiKeyCard`).
-   `src/features`: **User Scenarios.** Encapsulates pieces of business logic that provide value to the user, such as `CreateApiKey`, `AuthByCredentials`, or `UpdateUserProfile`. A feature is a combination of UI and logic that solves a single user story.
-   `src/widgets`: **Compositional Blocks.** Larger, independent UI blocks that compose features and entities into meaningful sections of the interface (e.g., `Header`, `PageLayout`, `ApiKeysTable`). They often have their own internal state but no business logic.
-   `src/pages`: **Application Pages.** The entry points for routes. A page is a simple composition of widgets, features, and entities. Pages should contain minimal logic and primarily serve to structure the layout.
-   `src/app`: **The Root.** The final layer that initializes the entire application. It contains the root component, global style providers (`ThemeProvider`), router setup, and other global configurations.

**Why FSD?**
-   **Controlled Scopes:** It enforces a strict "Public API" for each module (slice) via `index.ts` files. This hides implementation details and allows for safe refactoring within a slice without breaking other parts of the application.
-   **Low Coupling:** The layers can only depend on layers below them (e.g., a `feature` can use an `entity`, but not the other way around). This prevents "spaghetti code" and makes the architecture predictable.
-   **High Cohesion:** All code related to a single entity or feature is colocated, making it easy to find and work with.

### 3. State Management Strategy

We divide state into two distinct categories:

-   **Server State:** Any data that originates from the server. This is **exclusively** managed by **TanStack Query**. It is the single source of truth for all API data.
-   **Client State (UI State):** Data that exists only within the client.
    -   **Local Component State (`useState`):** The default choice. Used for simple state that is not shared, like the open/closed state of a modal (`const [isOpen, setIsOpen] = useState(false)`).
    -   **Global Client State (`Zustand` or `React Context`):** Used only for global, rarely-changing state that is needed across many disconnected parts of the application. A prime example is our `AuthContext`, which holds the authentication status of the user. We avoid using this for data that can be derived or fetched from the server.

### 4. Testing Philosophy

-   **Testing Pyramid:** We follow the standard testing pyramid, prioritizing different types of tests.
    1.  **Unit Tests (Vitest):** For small, pure functions and helper hooks in the `shared` layer. They are fast and easy to write.
    2.  **Integration Tests (Vitest + React Testing Library):** **This is our primary focus.** We test `features` and `widgets` by simulating user interactions. For example, we test that filling a form and clicking "Submit" calls the correct API hook, or that a table correctly renders provided data. We test from the user's perspective, not by inspecting implementation details.
    3.  **End-to-End (E2E) Tests (e.g., Playwright/Cypress):** To be implemented for critical user flows, such as the entire login process or the API key creation and deletion cycle.

This structured approach to architecture and development allows us to build a complex application that remains a pleasure to work on, easy to debug, and ready to scale for the future.
