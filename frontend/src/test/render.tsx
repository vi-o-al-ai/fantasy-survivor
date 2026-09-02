import { render } from "@testing-library/react";
import type { ReactElement } from "react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { ApiClientProvider } from "@/api/ApiProvider";
import type { ApiClient } from "@/api/client";

/** Render a page with a stub API client at a given route. */
export function renderPage(
  element: ReactElement,
  client: ApiClient,
  { path = "/", route = "/" }: { path?: string; route?: string } = {},
) {
  return render(
    <ApiClientProvider client={client}>
      <MemoryRouter initialEntries={[route]}>
        <Routes>
          <Route path={path} element={element} />
        </Routes>
      </MemoryRouter>
    </ApiClientProvider>,
  );
}
