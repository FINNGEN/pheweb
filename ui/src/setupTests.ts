import { vi } from 'vitest'

// tests were written for jest; vi has the same mock api
(globalThis as any).jest = vi
