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
