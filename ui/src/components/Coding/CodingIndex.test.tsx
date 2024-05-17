/* eslint-env jest */

import {createTitle} from "./CodingIndex";

test('coding title', async () => {
    expect(createTitle(undefined)).toBe("coding");
    expect(createTitle("TEST")).toBe("coding TEST");
})
