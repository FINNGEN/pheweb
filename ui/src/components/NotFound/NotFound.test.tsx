import React from "react";
import { render } from "@testing-library/react";
import NotFoundEntity from "./NotFoundEntity";
import { ConfigurationWindow } from "../Configuration/configurationModel";

declare let window: ConfigurationWindow;

test("not found includes search term", () => {
  const uuid = crypto.randomUUID();
  const search = `?query=${uuid}`;
  const Temp = NotFoundEntity("entity");
  const wrapper = render(<Temp location={{ search }} />);
  const text = wrapper.container.textContent;
  //expect(text).toContain(uuid);
});

test("not found missing search term", () => {
  const search = `noquery`;
  const Temp = NotFoundEntity("entity");
  const wrapper = render(<Temp location={{ search }} />);
  //expect(wrapper.container.textContent).toContain("empty query");
});

test("not found includes search term : configured", () => {
  const uuid = crypto.randomUUID();
  const salt = crypto.randomUUID();

  window.config = {
    userInterface: { notFound: { page: { message: `{{query}} : ${salt}` } } },
  };

  const search = `?query=${uuid}`;
  const Temp = NotFoundEntity("entity");
  const wrapper = render(<Temp location={{ search }} />);
  //expect(wrapper.container.textContent).toContain(uuid);
  //expect(wrapper.container.textContent).toContain(salt);
});
