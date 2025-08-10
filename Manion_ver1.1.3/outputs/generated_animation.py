from manim import *

class FactoringQuadraticEquations(Scene):
    def construct(self):
        # Introduction
        title = Text("Factoring Quadratic Equations", font_size=40, color=BLUE)
        self.play(Write(title))
        self.wait(2)
        self.play(FadeOut(title))

        # Equation Representation
        equation = MathTex("f(x) = ax^2 + bx + c")
        self.play(Write(equation))
        self.wait(2)

        # Factoring
        factored = MathTex("f(x) = a(x-d)(x-e)")
        self.play(Transform(equation, factored))
        self.wait(2)

        # Roots Extraction
        roots = MathTex("x = d, e")
        self.play(Transform(equation, roots))
        self.wait(2)

        # Final Cleanup
        self.play(FadeOut(equation))

def main():
    # Create the scene
    scene = FactoringQuadraticEquations()
    scene.render()

if __name__ == "__main__":
    main()