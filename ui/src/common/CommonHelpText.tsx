import React, { useState } from "react";
import { mustacheDiv } from "./commonUtilities";

/* show the first paragraph of the help, the rest behind a toggle */
const HelpText = ({ text }: { text: string }) => {
  const [expanded, setExpanded] = useState(false);
  const [first, ...rest] = text.split(/\n/);
  const hasMore = rest.join('').trim() !== '';
  const toggle = (e: React.MouseEvent) => {
    e.preventDefault();
    setExpanded(!expanded);
  };
  return (
    <div className="help-text">
      {mustacheDiv(expanded ? text : first, {})}
      {hasMore && <a href="#" onClick={toggle}>{expanded ? 'show less' : 'show more'}</a>}
    </div>
  );
}

export default HelpText;
