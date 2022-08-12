describe('a first spec', () => {
  it('has our title and a #cart', () => {
      cy.visit('localhost:8000')
      cy.title().should('eq', 'HTM Store')
      cy.get("#cart").click({force: true}).get(".h2")
  })
})
