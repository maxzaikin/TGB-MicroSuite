// file: src/app/App.tsx

import { AppRouter } from './router';
import { withProviders } from './providers';

/**
 * The root component of the app. It is responsible for composing and rendering the main router outlet.
 *
 * Wrapped with the `withProviders` HOC to inject all necessary global contexts (Theme, Router, React Query, Auth, etc.).
 * (Higher-Order Component) - 
 */
const App = () => {
  return (
    <div className="app">
      {/* The AppRouter component handles all page-level routing. */}
      <AppRouter />
    </div>
  );
};

export default withProviders(App);