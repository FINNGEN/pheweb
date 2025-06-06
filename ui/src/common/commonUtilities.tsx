import React, {useEffect} from "react";
import * as Handlebars from "handlebars/dist/cjs/handlebars";

export function toSorted<T>(array : T[],compareFn?: (a: T, b: T) => number) : T[] { array.sort(compareFn); return array; }
export const capitalizeFirstLetter = (input: string | null): string => input?.length ? input[0].toUpperCase() + input.slice(1) : "";

export const range = (start: number, end: number): number[] =>
    Array.from({ length: end - start + 1 }, (_, i) => start + i);

export function partition<T>(array: T[], predicate: (item: T) => boolean): [T[], T[]] {
    return array.reduce<[T[], T[]]>(
        ([pass, fail], item) => (predicate(item) ? [[...pass, item], fail] : [pass, [...fail, item]]),
        [[], []]
    );
}
/**
 * Compose function
 *
 * see : https://www.typescriptlang.org/docs/handbook/release-notes/typescript-3-4.html
 *
 * @param f
 * @param g
 */
export function compose<A, B, C>(
  f: (arg: A) => B,
  g: (arg: B) => C
): (arg: A) => C {
  return (x) => g(f(x));
}

export type Handler = (url : string) => (e : Error) => void
const defaultHandler : Handler = (url : string) => (e : Error) => {
  warn(url,e)
}

/**
 * Get url
 *
 * Takes a setter and an optional transformation and a fetchURL
 * Fetches url as a json object.  Calls the sink with the resulting
 * json.  If there is an error it's sent to the console.
 *
 * @param url
 * @param sink
 * @param fetchURL
 */
export function get<X,Y = void>(url: string,
                         sink: (x: X) => Y,
                         handler :  Handler= defaultHandler) : Promise<void | Y> {
  return fetch(url)
    .then((response) => {
      if (response.status === 200) {
        return response.json() as Promise<X>;
      } else {
        const msg = `${response.statusText}`;
        throw new Error(msg);
      }
    })
    .then(sink)
    .catch(handler(url));
};

/**
 * Delete url
 *
 * Takes a setter and an optional transformation and a fetchURL
 * Fetches url as a json object.  Calls the sink with the resulting
 * json.  If there is an error it's sent to the console.
 *
 * @param url
 * @param sink
 * @param fetchURL
 */


export const deleteRequest : <X>(url: string,
                                 sink: (x: X) => void,
                                 handler? :  Handler) => Promise<void> = (
    url,
    sink,
    handler = defaultHandler
) =>
    fetch(url, { method : 'DELETE' })
        .then((response) => {
          if (response.status === 200) {
            return response.json();
          } else {
            throw new Error(response.statusText);
          }
        })
        .then(sink)
        .catch(handler(url));

Handlebars.registerHelper('23toX', (x) => (x === 23 || x === '23')?'X':x);
Handlebars.registerHelper('isX', (x) => (x === 23 || x === '23' || x === 23 || x === 'X'));

/**
 * mustacheDiv
 *
 * return a div that contains as it's inner html
 * the output of a mustache template expanded using
 * the given context
 */
export const mustacheDiv: <X>(template: string, content: X) => JSX.Element = (
  template,
  content
) => (
  <div
    dangerouslySetInnerHTML={{ __html: Handlebars.compile(template)(content) }}
  ></div>
);

/**
 * Set the title of the page.
 *
 * @param title
 */
export const setPageTitle = (title : string) : void => {
    useEffect(() => {
        document.title = title;
    }, [title]);
};
/**
 * mustacheSpan
 *
 * return a span that contains as it's inner html
 * the output of a mustache template expanded using
 * the given context
 */
export const mustacheSpan: <X>(template: string, content: X) => JSX.Element = (
  template,
  content
) => (
  <span
    dangerouslySetInnerHTML={{ __html: Handlebars.compile(template)(content) }}
  ></span>
);

/**
 * mustacheText
 *
 * return a span that contains as it's inner html
 * the output of a mustache template expanded using
 * the given context
 */
export const mustacheText: <X>(template: string, content: X) => string = (
  template,
  content
) => Handlebars.compile(template)(content);


export const fatal = (msg : string, context : {} ={}) : never =>{
  console.log(msg);
  alert(msg);
  console.log(context);
  throw msg;
}

export const warn = (msg : string, context : {} ={}) : void =>{
  console.warn(msg);
  console.log(context);
}
/**
 * flatten a list.
 * note this assumes expressions are well-typed and excludes null and undefined.
 * switch to .flat when upgrade to js 2019.
 */
export const flatten : <X>(a : X[][]) => X[] = (l) => l.reduce((a, v) =>a.concat(v),[]);
export const defaultEmptyArray : <X,Y>(a : X[],defaultArray :Y[]) => (X|Y)[] = (a,defaultArray) => a.length == 0?defaultArray:a;

export const isNonEmptyArray : <X>(value : X) => boolean = (value) => Array.isArray(value) && value.length > 0;
