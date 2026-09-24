import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ScoreBar } from "./score-bar";

describe("ScoreBar", () => {
  it("renders the label and score text", () => {
    render(<ScoreBar label="Skills" score={82} />);
    expect(screen.getByText("Skills")).toBeInTheDocument();
    expect(screen.getByText("82/100")).toBeInTheDocument();
  });

  it("sets the fill width proportional to the score", () => {
    render(<ScoreBar label="Experience" score={45} />);
    expect(screen.getByTestId("score-bar-fill").style.width).toBe("45%");
  });

  it("clamps an out-of-range score into 0-100 for the bar width", () => {
    const { rerender } = render(<ScoreBar label="X" score={150} />);
    expect(screen.getByTestId("score-bar-fill").style.width).toBe("100%");

    rerender(<ScoreBar label="Y" score={-10} />);
    expect(screen.getByTestId("score-bar-fill").style.width).toBe("0%");
  });
});
