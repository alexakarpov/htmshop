describe('a first spec', () => {
  beforeEach(() => {
    cy.visit('localhost:8000')
  })

  it('has our title', () => {
    cy.title().should('eq', 'HTM Store')
  })

  it('a #cart redirecting to /basket/', () => {
    // force - because "it's covered by another element (Django Debug Toolbar)
    cy.get("#cart").click({force: true})
                   .get(".h2")
                   .contains('Your Cart')
                   .url().should('include', '/basket/')
  })
})

describe('wheee, a second spec', () => {
  it('another spec', () => {
      cy.visit('localhost:8000')
      cy.title().should('eq', 'HTM Store')
  })
})

describe("Login", () => {
  before(() => {
    cy.fixture("accounts.json").as("mockedUsers");
  });

  it("Can login through the UI", function () {
    cy.visit("localhost:8000/accounts/login/");
    cy.get("input[name='email']").type(this.mockedUsers[1].fields.email);
    cy.get("input[name='password']").type("pass");
    cy.get(".account-form").submit();
    cy.getCookie("sessionid").should("exist");
    cy.get("#dashboard_title").should('have.text', 'Your Account (alexandre.karpov@protonmail.com)');
  });
});