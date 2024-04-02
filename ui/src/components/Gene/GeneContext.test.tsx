import {createTitle} from "./GeneContext";

test('gene title', async () => {
    expect(createTitle("APOE", undefined)).toBe("gene APOE");
    expect(createTitle("APOE", "TEST")).toBe("gene APOE TEST");
})
