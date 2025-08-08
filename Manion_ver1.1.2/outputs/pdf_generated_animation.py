from manim import *

class PolynomialFactorization(Scene):
    def construct(self):
        # Introduction
        title = Text("Polynomial Factorization", color=BLUE).scale(1.5)
        self.play(Write(title))
        self.wait(2)
        self.play(FadeOut(title))

        # Initial expression
        expression = MathTex("x^3 - 3x^2 - 4x + 12")
        self.play(Write(expression))
        self.wait(2)

        # Grouping terms
        grouped_terms = VGroup(
            MathTex("(x^3 - 3x^2)"), 
            MathTex(" + "), 
            MathTex("(-4x + 12)")
        ).arrange(RIGHT)
        self.play(Transform(expression, grouped_terms))
        self.wait(2)

        # factoring each group
        factored_groups = VGroup(
            MathTex("x^2(x - 3)"), 
            MathTex(" + "), 
            MathTex("-4(x - 3)")
        ).arrange(RIGHT)
        self.play(Transform(expression, factored_groups))
        self.wait(2)

        # Combining with common factors
        combined_common_factors = MathTex("(x^2 - 4)(x - 3)")
        self.play(Transform(expression, combined_common_factors))
        self.wait(2)

        # Further factorization
        further_factored = MathTex("(x - 2)(x + 2)(x - 3)")
        self.play(Transform(expression, further_factored))
        self.wait(3)

        # Roots of the polynomial
        roots = Tex("Roots of the polynomial: ", "$x = 3$", ", ", "$x = 2$", ", ", "$x = -2$").scale(0.5)
        roots.next_to(expression, DOWN)
        self.play(Write(roots))

        self.wait(3)
        # Cleanup
        self.play(FadeOut(expression), FadeOut(roots))

# To render the scene, run:
# manim -p -ql PolynomialFactorization.py PolynomialFactorization